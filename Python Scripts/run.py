import os
import sys
import shutil
import glob

#The first inp step file is written by hand, later iterations will use the gmesh converter directly.
def run_first_step(ccx_exe_path,inp_directory):
  os.chdir(inp_directory)
  dir_path = inp_directory
  for root, dirs, files in os.walk(dir_path):
    for file in files:
      if file.endswith('.inp'):
        inp_file_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
  os.system(ccx_exe_path+" "+inp_file_name)
  #monitor=""
  #while "Job Finished" not in monitor and "*ERROR" not in monitor: #need to add an error check, in case there're issue with the inp, rin files, or anything else
  #  monitor=sys.stdout

  
def copy_rename_rout_to_rin(new_step_folder_name, rout_file_dir,new_step_name):
  # New step folder path
  new_path = os.path.join(rout_file_dir, new_step_folder_name)
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
    shutil.copy(rout_file_dir,new_path) #copy the file to the new folder

    copied_rout_file = os.path.join(new_path,rout_file_name)#build the new path for the rout file
    new_rin_file_name = os.path.join(new_path, new_step_name+".rin")#define the new step file name, this name must be the same as the inp file, here new_step_name 

    os.rename(copied_rout_file, new_rin_file_name)#rename
  except OSError as error:
    print(error)


  
  
  

  
  
  
  src = rout_file_path
  dest = new_step_file_dir
  par = "*"
  i=1
  d = []
  for file in glob.glob(os.path.join(src,par)):#for all file in the src directory
    f = str(file).split('\\')[-1]#take f as the file name with extension
    for n in glob.glob(os.path.join(dest,par)):#for all files in the dest directory
        d.append(str(n).split('\\')[-1])# the d string with all the dest directory file name with extension
    if f not in d:
        print("copied",f," to ",dest)#notify the user that the file was successfully copied to the dest, with no duplicate existing
        shutil.copy(file,dest)
    else:
        f1 = str(f).split(".")
        f1 = f1[0]+"_"+str(i)+"."+f1[1]
        while f1 in d:
            f1 = str(f).split(".")
            f1 = f1[0]+"_"+str(i)+"."+f1[1]
            print("{} already exists in {}".format(f1,dest))
            i =i + 1
        shutil.copy(file,os.path.join(dest,f1))
        print("renamed and copied ",f1 ,"to",dest)
        i = 1
  
