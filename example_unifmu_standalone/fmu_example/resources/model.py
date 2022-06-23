import numpy as np
import pickle
from fmi2 import Fmi2FMU, Fmi2Status


class Model(Fmi2FMU):
    def __init__(self) -> None:
        
        # Matches modelDescription.xml
        reference_to_attribute = {
            0: "Uio",
            1: "Tio",
            2: "Fio",
            3: "RNio",
        }
        
        super().__init__(reference_to_attribute)
                     
        self.KN = np.array([[20/6]]) * 0.5 # N/mm
        self.FN = np.array([[8.0]])

        # FMU i/o
        self.U = np.zeros(shape=(1,1))
        self.T = np.zeros(shape=(1,1))
        self.F = np.zeros(shape=(1,1))
        self.RN = np.zeros(shape=(1,1))

        self.Uio = float(self.U)
        self.Tio = float(self.T)
        self.Fio = float(self.F)
        self.RNio = float(self.RN)

        self._update_outputs()

    def serialize(self):

        bytes = pickle.dumps(
            (
                self.Uio,
                self.Tio,
                self.Fio,
            )
        )
        return Fmi2Status.ok, bytes

    def deserialize(self, bytes) -> int:
        (
            Uio,
            Tio,
            Fio,
        ) = pickle.loads(bytes)
        self.Uio = Uio
        self.Tio = Tio
        self.Fio = Fio

        self._update_outputs()

        return Fmi2Status.ok

    def _update_outputs(self):
        # Feedthrough stuff is implemented here.
        '''
        self.real_c = self.real_a + self.real_b
        self.integer_c = self.integer_a + self.integer_b
        self.boolean_c = self.boolean_a or self.boolean_b
        self.string_c = self.string_a + self.string_b
        '''

    def do_step(self, current_time, step_size, no_step_prior):
                
        # read input
        self.U = np.matrix(self.Uio)
        self.F = np.matrix(self.Fio)
        
        # compute total force
        self.RN = self.KN.dot(self.U) - self.FN * self.F
        self.RNio = float(self.RN)

        self._update_outputs()

        return Fmi2Status.ok

if __name__ == "__main__": # <--- ensures that test-code is not run if module is imported

    import matplotlib.pyplot as plt

    dt = 1.0 # time step [s]
    step = 100 # Simulation steps.
    tmax = (step-1) * dt # Simulation length.
    t = np.linspace(0.0, tmax, step) # Time axis.
    f = np.sin(2*np.pi*t/tmax)       
    u = np.linspace(0.0, 20.0, step)
    
    # create FMU
    myModel = Model()
    
    # output
    RN = np.zeros(step)
    
    for idx, ti in enumerate(t):
        
        myModel.Uio = u[idx]
        myModel.Fio = f[idx]
        myModel.do_step(ti, dt, False)
        RN[idx] = myModel.RNio

    plt.plot(t, RN)
    plt.ylabel("RN")
    plt.xlabel("t")
    plt.show()