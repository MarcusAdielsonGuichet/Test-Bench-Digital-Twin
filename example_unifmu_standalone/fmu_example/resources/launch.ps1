$Venvfolder = '_fmu_env_'
"Test to see if folder $Venvfolder exists"
if (Test-Path -Path $Venvfolder) {
} else {
  "Creating virtual environment"
  & python -m venv "$Venvfolder"
  & ".\$Venvfolder\Scripts\Activate.ps1"
  & pip install wheel
  & python -m pip install protobuf==3.20.0
  & python -m pip install unifmu[python-backend]
  & python -m pip install numpy
  & python -m pip install matplotlib
}
& ".\$Venvfolder\Scripts\Activate.ps1"
& python backend.py