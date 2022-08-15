from pathlib import Path
import os

current_path=Path(__file__).resolve()#repr() reads the string as raw characters
folders=os.path.split(current_path)[0]
os.chdir(folders)
print(folders)
ccx_path="./../CCX Files/calculix2.19win64/ccx/ccx_219.exe"
os.chdir(ccx_path)
print(os.getcwd())
