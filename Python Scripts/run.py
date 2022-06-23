import os
#The first inp step file is written by hand, later iterations will use the gmesh converter directly.
def run(ccx_exe_path,inp_directory):
  os.system('cmd /k cd '+inp_directory)
  dir_path = inp_directory
  for root, dirs, files in os.walk(dir_path):
    for file in files:
      if file.endswith('.inp'):
        inp_file_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
  os.system('cmd /k '+ccx_exe_path+" "+inp_file_name)
  
