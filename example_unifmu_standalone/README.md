Run in this folder:
#Create the virtual env
python -m venv venv
#Activate the virtual env
.\venv\Scripts\Activate.ps1

#Install the wheel package
pip install wheel

Upgrade pip if asked
#Install fmpy with all dependencies, can just be pip install fmpy[complete]
python -m pip install fmpy[complete]

#Install fmu with all dependencies
python -m pip install unifmu[python-backend]


Now there are two ways to test the FMU:
- Run python code directly: python .\fmu_example\resources\model.py  
- Run powershell as admin, with set-executionpolicy unrestrited, as select No
- Load and run the FMU using the FMpy library: python run_fmu.py

You should test the code with both approaches.
