from fmpy import read_model_description
from fmpy.fmi2 import FMU2Slave
import numpy as np
import os
import matplotlib.pyplot as plt

if __name__ == "__main__": # <--- ensures that test-code is not run if module is imported
    
  fmu_filename = 'fmu_example'

  dt = 1.0 # time step [s]
  step = 100 # Simulation steps.
  tmax = (step-1) * dt # Simulation length.
  t = np.linspace(0.0, tmax, step) # Time axis.
  
  # Inputs
  f = np.sin(2*np.pi*t/tmax)       
  u = np.linspace(0.0, 20.0, step)

  # read the model description
  model_description = read_model_description(fmu_filename)

  # collect the value references
  vrs = {}
  for variable in model_description.modelVariables:
    vrs[variable.name] = variable.valueReference

  # get the value references for the variables we want to get/set
  vr_Uio = vrs['Uio']  
  vr_Tio = vrs['Tio']  
  vr_Fio = vrs['Fio']
  vr_RNio = vrs['RNio']
  
  # output
  RN = np.zeros(step)

  fmu = FMU2Slave(guid=model_description.guid,
                    unzipDirectory=os.path.abspath(fmu_filename),
                    modelIdentifier=model_description.coSimulation.modelIdentifier,
                    instanceName='instance1')
  
  # initialize
  fmu.instantiate()
  fmu.setupExperiment(startTime=t[0])
  fmu.enterInitializationMode()
  fmu.exitInitializationMode()

  i = 0

  # simulation loop
  while i < step:

    # NOTE: the FMU.get*() and FMU.set*() functions take lists of
    # value references as arguments and return lists of values

    # set the input
    fmu.setReal([vr_Uio, vr_Fio], [u[i], f[i]])

    # perform one step
    fmu.doStep(currentCommunicationPoint=t[i], communicationStepSize=dt)

    # get the result
    RN[i] = fmu.getReal([vr_RNio])[0]

    # advance the time
    i += 1

  
  fmu.terminate()
  fmu.freeInstance()

plt.plot(t, RN)
plt.ylabel("RN")
plt.xlabel("t")
plt.show()
