import os
import sys
import shutil
import glob
import subprocess
import numpy as np
import tempfile

ccx_exe_path=r"C:\Users\marcu\OneDrive\Desktop\calculix2.19win64\ccx\ccx_219.exe"
work_dir=tempfile.mkdtemp()
rout_dir=r"C:\Users\marcu\OneDrive\Desktop\test\run_test\Step_1"
# step_dir=r"C:\Users\marcu\OneDrive\Desktop\test\force_disp_dat"

#test values
[first_increment_value,step_duration,min_increment_value,max_increment_value]=[1E-8,1,1E-12,0.005]
[output_type,disp_value]=["Disp",20]
disp_node_set_name="ConstraintDisplacement"
fixed_node_set_name="ConstraintFixed"
first_degree_freedom=last_degree_freedom=1
total_steps=20


#The first inp step file is written by hand, later iterations will use the gmesh converter directly.
#Verified with comented section, takes 1-2 min for 20 steps with matrix generations and same values of disp for each step, however last folder stays active in the manager so need to kill the process once over
def run_simulation(ccx_exe_path,work_dir,rout_dir):
  os.chdir(rout_dir)
  for root, dirs, files in os.walk(rout_dir):
    for file in files:
      if file.endswith('.inp'):#hypothesis that there is only one inp file per step directory
        inp_file_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
        inp_file_path=os.path.join(rout_dir,file)
        break
    else:
      continue
    break
  
  # run solver
  output=subprocess.run(
      [ccx_exe_path,"-i",inp_file_name],
      capture_output=True,
      check=True,
      encoding='utf-8'
  ).stdout
  calculation_end="Job finished"
  if calculation_end not in output:
    return output
  else:
    error=False
    step_dir=rout_dir
    
    for i in range(2,total_step+1):
      if error==False:
        new_step_folder_name=f"Step_{i}"
        new_step_name=f"init_Step_{i}"
        
        #Procedure for the *RESTART function, check ccx manual for more info
        step_dir=copy_rename_rout_to_rin(work_dir,
        rout_file_dir,
        new_step_folder_name,
        new_step_name)
        
        #Generate and run the new step inp
        new_step_inpfile_writer(step_dir,
        first_increment_value,
        step_duration,
        min_increment_value,
        max_increment_value,
        new_step_name,
        output_type)
        
        out=run_inp_file(ccx_exe_path,
        step_dir,
        new_step_name)
      else:
        return out
    return f"{out}\nJob done, no issues"

def get_disp_characteristics(inp_file_path):
  return disp_node_set_name,first_degree_freedom,last_degree_freedom
  
def read_and_send_outputs(step_dir):
  return mass_matrix, stiff_matrix, disp_values

def update_inputs(other_fmu):
  return first_increment_value,step_duration,min_increment_value,max_increment_value,new_step_name,output_type,new_disp_value
  
#verified and working
def copy_rename_rout_to_rin(work_dir,rout_dir,new_step_folder_name, new_step_name):
  # New step folder path
  step_dir = os.path.join(work_dir, new_step_folder_name)
  # Create the directory
  try:
    os.mkdir(step_dir)
    for root, dirs, files in os.walk(rout_dir):#search inside the dir
      for file in files:
          if file.endswith('.rout'):
              rout_file_name=file
              break
      else:
        continue
      break
    rout_path = os.path.join(rout_file_dir, rout_file_name)#build the complete path for the rout file
    shutil.copy(rout_path,step_dir) #copy the file to the new folder

    copied_rout_file = os.path.join(step_dir,rout_file_name)#build the new path for the rout file
    new_rin_file_name = os.path.join(step_dir, new_step_name+".rin")#define the new step file name, this name must be the same as the inp file, here new_step_name 

    os.rename(copied_rout_file, new_rin_file_name)#rename
    return new_path
  except: #OSError as error:
      shutil.rmtree(step_dir)
      os.mkdir(step_dir)
      for root, dirs, files in os.walk(rout_dir):#search inside the dir for the rout file
          for file in files:
              if file.endswith('.rout'):
                  rout_file_name=file
                  break
              else:
                  continue
          break
      rout_path = os.path.join(rout_dir, rout_file_name)#build the complete path for the rout file
      shutil.copy(rout_path,step_dir) #copy the file to the new folder

      copied_rout_file = os.path.join(step_dir,rout_file_name)#build the new path for the rout file
      new_rin_file_name = os.path.join(step_dir, new_step_name+".rin")#define the new step file name, this name must be the same as the inp file, here new_step_name

      os.rename(copied_rout_file, new_rin_file_name)#rename
      rout_dir=step_dir
      return step_dir

#verified and working
def new_step_inpfile_writer(step_dir,first_increment_value,step_duration,min_increment_value,max_increment_value,new_step_name,output_type):#needs a previous run, rename the last_step.rout into new_inp_file.rin 
  
  new_inp=open(os.path.join(step_dir, new_step_name+".inp"), 'w')
  #Continuing the previous step calculation
  new_inp.write("*RESTART, READ\n")
  
  #Step characteristics and analysis type
  new_inp.write("*STEP, INC=1000000\n")
  new_inp.write("*STATIC\n")
  new_inp.write(f"{first_increment_value},{step_duration},{min_increment_value},{max_increment_value}\n")
  
  #Saving the calculation for next step
  new_inp.write("*RESTART, WRITE\n")
  
  #Displaced nodes characteristics 
  new_inp.write("*BOUNDARY\n")
  new_inp.write(f"{disp_node_set_name},{first_degree_freedom},{last_degree_freedom},{disp_value}\n")
  
  #Fixed nodes
  new_inp.write("*BOUNDARY\n")
  new_inp.write(f"{fixed_node_set_name},1,6,0\n")
  
  #Output files and values
  new_inp.write(f"*NODE PRINT, NSET={disp_node_set_name}")
  if output_type=="Disp":
    new_inp.write("\nU\n")
  elif output_type=="Force":
    new_inp.write(",Totals=Only\nRF\n")
    
  new_inp.write("*END STEP\n")
  
  #Mass and stiffness storage
  new_inp.write("*STEP\n")
  new_inp.write("*FREQUENCY, SOLVER=MATRIXSTORAGE\n")
  new_inp.write("*END STEP")
  new_inp.close()

def step_inpfile_writer(filename):#needs a previous run, rename the last_step.rout into new_inp_file.rin
    line_number=0
    with open(filename, 'r+') as new_inp:
        lines=new_inp.readlines()
        new_inp.seek(0)
        new_inp.truncate()
        for line_nb,line in enumerate(lines):
            if "*SOLID SECTION"  in line:
                line_number=line_nb
                print(line_number)
                break
        stop=line_number+1
        print(lines[:stop])
        new_inp.writelines(lines[:stop])
#verified and functional
def runtest(ccx_exe_path,work_dir,rout_dir):
  os.chdir(rout_dir)
  for root, dirs, files in os.walk(rout_dir):
    for file in files:
      if file.endswith('.inp'):#hypothesis that there is only one inp file per step directory
        inp_file_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
        inp_file_path=os.path.join(rout_dir,file)
        break
    else:
      continue
    break
  
  # run solver
  output=subprocess.run(
      [ccx_exe_path,"-i",inp_file_name],
      capture_output=True,
      check=True,
      encoding='utf-8'
  ).stdout
  calculation_end="Job finished"
  if calculation_end in output:
    return "No error"
  else:
    return output #best would be to show the error instead
  
def run_inp_file(ccx_exe_path,step_dir,new_step_name):
  os.chdir(step_dir)
  output=subprocess.run(
      [ccx_exe_path,"-i",new_step_name],
      capture_output=True,
      check=True,
      encoding='utf-8'
  ).stdout
  calculation_end="Job finished"
  if calculation_end not in output:
    error=True
  return output


        # #send the outputs to the other FMU
        # mass_matrix,
        # stiff_matrix,
        # disp_values=read_and_send_outputs(step_dir)#need to read the .mas, .sti, .dat files and send corresponding outputs types to the other FMU, need more info on orchestrator for that
        
        # #update the FMU inputs
        # first_increment_value,
        # step_duration,
        # min_increment_value,
        # max_increment_value,
        # output_type,
        # new_disp_value=update_inputs(other_fmu)#User defined? Orchestrator defined?

    # disp_node_set_name,
    # first_degree_freedom,
    # last_degree_freedom=get_disp_characteristics(inp_file_path)#need to read the inp file and extract the corresponding values and names
# 
# 
# try:
#     shutil.rmtree(dir_path)
# except OSError as e:
#     print("Error: %s : %s" % (dir_path, e.strerror))


# #verified and working, but obsolete if we use subprocess.run instead
# def run_inp_file(ccx_exe_path, step_dir, new_step_name):
#   os.chdir(step_dir)
#   os.system(ccx_exe_path+" "+new_step_name)
#   
# def runtest(ccx_exe_path,work_dir,rout_dir):
#   os.chdir(rout_dir)
#   for root, dirs, files in os.walk(rout_dir):
#     for file in files:
#       if file.endswith('.inp'):#hypothesis that there is only one inp file per step directory
#         inp_file_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
#         inp_file_path=os.path.join(rout_dir,file)
#         break
#     else:
#       continue
#     break
#   
#   # run solver
#   _process = subprocess.Popen(
#       [ccx_exe_path,"-i",inp_file_name],
#       cwd=rout_dir,
#       stdout=subprocess.PIPE,
#       stderr=subprocess.PIPE
#   )
#   ccx_output, ccx_err=_process.communicate()
#   calculation_end="Job finished"
#   ce=calculation_end.encode('utf-8')
#   if ce in ccx_output:
#     return "No error"
#   else:
#     return ccx_output #best would be to show the error instead
#   
  
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
