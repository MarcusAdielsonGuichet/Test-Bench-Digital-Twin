$Venvfolder = '_fmu_env_'
"Test to see if folder $Venvfolder exists"
if (Test-Path -Path $Venvfolder) {
} else {
  "Creating virtual environment"
  & python -m venv "$Venvfolder"
  & ".\$Venvfolder\Scripts\Activate.ps1"
  & pip install wheel
  & python -m pip install unifmu[python-backend]
}
& ".\$Venvfolder\Scripts\Activate.ps1"
& python backend.py