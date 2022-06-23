Run in this folder:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install wheel
Upgrade pip if asked
python -m pip install fmpy[complete]
python -m pip install unifmu[python-backend]


Now there are two ways to test the FMU:
- Run python code directly: python .\fmu_example\resources\model.py  
- Load and run the FMU using the FMpy library: 

You should test the code with both approaches.
