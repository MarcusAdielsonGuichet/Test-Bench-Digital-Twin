import os

def run(ccx_exe_path,inp_path):
  os.system('cd '+ccx_exe_path)
  inp_file_name=os.path.splitext(os.path.basename(file))[0]#not
  os.system('cmd /k ccx '+inp_file_name)
