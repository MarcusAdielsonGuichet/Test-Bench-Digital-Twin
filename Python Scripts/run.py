import os
import sys
import shutil
import glob
import subprocess



ccx_exe_path=r"C:\Users\marcu\OneDrive\Desktop\calculix2.19win64\ccx\ccx_219.exe"
work_dir=r"C:\Users\marcu\OneDrive\Desktop\test\run_test"
first_inp_directory=r"C:\Users\marcu\OneDrive\Desktop\test\run_test\Step_1"

#test values
[first_increment_value,step_duration,min_increment_value,max_increment_value]=[1E-8,1,1E-12,0.005]
[output_type,disp_value]=["Disp",20]
disp_node_set_name="ConstraintDisplacement"
fixed_node_set_name="ConstraintFixed"
first_degree_freedom=last_degree_freedom=1



#The first inp step file is written by hand, later iterations will use the gmesh converter directly.
def run(ccx_exe_path,work_dir,first_inp_directory):
  os.chdir(first_inp_directory)
  for root, dirs, files in os.walk(first_inp_directory):
    for file in files:
      if file.endswith('.inp'):#hypothesis that there is only one inp file per step directory
        inp_file_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
        inp_file_path=os.path.join(first_inp_directory,file)
        break
    else:
      continue
    break
  os.system(ccx_exe_path+" "+inp_file_name)
  
  
  
  #This is the code from FreeCAD
  # run solver
  _process = subprocess.Popen(
      [ccx_exe_path, "-i ", inp_file_name],
      cwd=self.directory,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
  )
  #self.signalAbort.add(self._process.terminate)
  _process.communicate()
  #self.signalAbort.remove(self._process.terminate)
  
  
  
  #Need to build and add a monitor to check if there are no issue with the files, with the subprocess module function, and continue only if the previous step has been completed
  rout_file_dir=first_inp_directory
  step_dir=first_inp_directory
  [Disp_node_set_name,
   first_degree_freedom,
   last_degree_freedom]=get_disp_characteristics(inp_file_path)
  for i in range(2,total_step+1):
    #send the outputs for new input calc in the other FMU
    [mass_matrix,
     stiff_matrix,
     disp_values]=read_and_send_outputs(step_dir)
    
    #update the FMU inputs, with those received from the other FMU
    [first_increment_value,
     step_duration,
     min_increment_value,
     max_increment_value,
     output_type,
     new_disp_value]=update_inputs(other_fmu)
    
    new_step_folder_name="Step_"+i
    new_step_name="init_Step_"+i
    
    #Procedure for the *RESTART function, check ccx manual for more info
    step_dir=copy_rename_rout_to_rin(work_dir,
                                     rout_file_dir,
                                     new_step_folder_name,
                                     new_step_name)
    
    #Generate and run the new step inp
    write_new_step_inpfile_with_restart_read_write(first_increment_value,
                                                   step_duration,
                                                   min_increment_value,
                                                   max_increment_value,
                                                   new_step_name,output_type)
    run_inp_file(ccx_exe_path,
                 step_dir,
                 new_step_name)

def read_and_send_outputs(step_dir):
  return mass_matrix, stiff_matrix, disp_values

def update_inputs(other_fmu):
  return first_increment_value,step_duration,min_increment_value,max_increment_value,new_step_name,output_type,new_disp_value
  
#verified and working
def copy_rename_rout_to_rin(work_dir,rout_file_dir,new_step_folder_name, new_step_name):
  # New step folder path
  new_path = os.path.join(work_dir, new_step_folder_name)
  # Create the directory
  try:
    os.mkdir(new_path)
    for root, dirs, files in os.walk(rout_file_dir):#search inside the dir
      for file in files:
          if file.endswith('.rout'):
              rout_file_name=file
              break
      else:
        continue
      break
    rout_path = os.path.join(rout_file_dir, rout_file_name)#build the complete path for the rout file
    shutil.copy(rout_path,new_path) #copy the file to the new folder

    copied_rout_file = os.path.join(new_path,rout_file_name)#build the new path for the rout file
    new_rin_file_name = os.path.join(new_path, new_step_name+".rin")#define the new step file name, this name must be the same as the inp file, here new_step_name 

    os.rename(copied_rout_file, new_rin_file_name)#rename
    return new_path
  except OSError as error:
    print(error)

#verified and working, doesn't include Matrix storage
def write_new_step_inpfile_with_restart_read_write(step_dir,first_increment_value,step_duration,min_increment_value,max_increment_value,new_step_name,output_type):#needs a previous run, rename the last_step.rout into new_inp_file.rin 
  
  new_inp=open(os.path.join(step_dir, new_step_name+".inp"), 'w')
  #Continuing the previous step calculation
  new_inp.write("*RESTART, READ\n")
  
  #Step characteristics and analysis type
  new_inp.write("*STEP, INC=1000000\n")
  new_inp.write("*DYNAMIC\n")
  new_inp.write(str(first_increment_value)+","+str(step_duration)+","+str(min_increment_value)+","+str(max_increment_value)+"\n")
  
  #Saving the calculation for next step
  new_inp.write("*RESTART, WRITE\n")
  
  #Displaced nodes characteristics 
  new_inp.write("*BOUNDARY\n")
  new_inp.write(disp_node_set_name+","+str(first_degree_freedom)+","+str(last_degree_freedom)+","+str(disp_value)+"\n")
  
  #Fixed nodes
  new_inp.write("*BOUNDARY\n")
  new_inp.write(fixed_node_set_name+",1,6,0\n")
  
  #Output files and values
  new_inp.write("*NODE PRINT, NSET="+disp_node_set_name)
  if output_type=="Disp":
    new_inp.write("\nU\n")
  elif output_type=="Force":
    new_inp.write(",Totals=Only\nRF\n")
    
  new_inp.write("*END STEP")
  new_inp.close()

#verified and working
def run_inp_file(ccx_exe_path, step_dir, new_step_name):
  os.chdir(step_dir)
  os.system(ccx_exe_path+" "+new_step_name)
  
def runtest(ccx_exe_path,work_dir,first_inp_directory):
  os.chdir(first_inp_directory)
  for root, dirs, files in os.walk(first_inp_directory):
    for file in files:
      if file.endswith('.inp'):#hypothesis that there is only one inp file per step directory
        inp_file_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
        inp_file_path=os.path.join(first_inp_directory,file)
        break
    else:
      continue
    break
  
  # run solver
  _process = subprocess.Popen(
      [ccx_exe_path,"-i",inp_file_name],
      cwd=first_inp_directory,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
  )
  ccx_output, ccx_err=_process.communicate()
  calculation_end="Job finished"
  ce=calculation_end.encode('utf-8')
  if ce in ccx_output:
    return "No error"
  else:
    return ccx_output #best would be to show the error instead

  

  
  
  # 
  # src = rout_file_path
  # dest = new_step_file_dir
  # par = "*"
  # i=1
  # d = []
  # for file in glob.glob(os.path.join(src,par)):#for all file in the src directory
  #   f = str(file).split('\\')[-1]#take f as the file name with extension
  #   for n in glob.glob(os.path.join(dest,par)):#for all files in the dest directory
  #       d.append(str(n).split('\\')[-1])# the d string with all the dest directory file name with extension
  #   if f not in d:
  #       print("copied",f," to ",dest)#notify the user that the file was successfully copied to the dest, with no duplicate existing
  #       shutil.copy(file,dest)
  #   else:
  #       f1 = str(f).split(".")
  #       f1 = f1[0]+"_"+str(i)+"."+f1[1]
  #       while f1 in d:
  #           f1 = str(f).split(".")
  #           f1 = f1[0]+"_"+str(i)+"."+f1[1]
  #           print("{} already exists in {}".format(f1,dest))
  #           i =i + 1
  #       shutil.copy(file,os.path.join(dest,f1))
  #       print("renamed and copied ",f1 ,"to",dest)
  #       i = 1
  # 
