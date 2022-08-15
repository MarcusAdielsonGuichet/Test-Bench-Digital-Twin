from pathlib import Path
import os

#repr() reads the string as raw characters

#Finding the path of the python script
current_path=Path(__file__).resolve()
folders=os.path.split(current_path)[0]
os.chdir(folders)
os.chdir("../")

#Saving the repository folder
rep_folder=os.getcwd()
print(rep_folder)

#Setting the ccx.exe path
ccx_path="./CCX Files/calculix2.19win64/ccx"
os.chdir(ccx_path)
ccx_path=os.path.join(os.getcwd(),"ccx_219.exe\n")
print(ccx_path)
os.chdir(rep_folder)

#Setting the working dir
work_dir="./CCX Files/test_runs"
os.chdir(work_dir)
work_dir=os.getcwd()
print(work_dir)
os.chdir(rep_folder)


#Setting the 1st inp folder
rout_dir="./CCX Files/test_runs/Step_1"
os.chdir(rout_dir)
rout_dir=os.getcwd()
print(rout_dir)