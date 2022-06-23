import pickle
import numpy as np


class Model:
    def __init__(self) -> None:
        # Matches modelDescription.xml
        self.reference_to_attribute = {
            0: "Uio",
            1: "Tio",
            2: "Fio",
            3: "RNio",
        }
        
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

    def fmi2DoStep(self, current_time, step_size, no_step_prior):
            
        # read input
        self.U = np.matrix(self.Uio)
        self.F = np.matrix(self.Fio)
        
        # compute total force
        self.RN = self.KN.dot(self.U) - self.FN * self.F
        self.RNio = float(self.RN)

        self._update_outputs()

        return Fmi2Status.ok

    def fmi2EnterInitializationMode(self):
        return Fmi2Status.ok

    def fmi2ExitInitializationMode(self):
        self._update_outputs()
        return Fmi2Status.ok

    def fmi2SetupExperiment(self, start_time, stop_time, tolerance):
        return Fmi2Status.ok

    def fmi2SetReal(self, references, values):
        return self._set_value(references, values)

    def fmi2SetInteger(self, references, values):
        return self._set_value(references, values)

    def fmi2SetBoolean(self, references, values):
        return self._set_value(references, values)

    def fmi2SetString(self, references, values):
        return self._set_value(references, values)

    def fmi2GetReal(self, references):
        return self._get_value(references)

    def fmi2GetInteger(self, references):
        return self._get_value(references)

    def fmi2GetBoolean(self, references):
        return self._get_value(references)

    def fmi2GetString(self, references):
        return self._get_value(references)

    def fmi2Reset(self):
        return Fmi2Status.ok

    def fmi2Terminate(self):
        return Fmi2Status.ok

    def fmi2ExtSerialize(self):

        bytes = pickle.dumps(
            (
                self.Uio,
                self.Tio,
                self.Fio,
            )
        )
        return Fmi2Status.ok, bytes

    def fmi2ExtDeserialize(self, bytes) -> int:
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

    def _set_value(self, references, values):

        for r, v in zip(references, values):
            setattr(self, self.reference_to_attribute[r], v)

        return Fmi2Status.ok

    def _get_value(self, references):

        values = []

        for r in references:
            values.append(getattr(self, self.reference_to_attribute[r]))

        return Fmi2Status.ok, values

    def _update_outputs(self):
        # Feedthrough stuff is implemented here.
        '''
        self.real_c = self.real_a + self.real_b
        self.integer_c = self.integer_a + self.integer_b
        self.boolean_c = self.boolean_a or self.boolean_b
        self.string_c = self.string_a + self.string_b
        '''


class Fmi2Status:
    """Represents the status of the FMU or the results of function calls.

    Values:
        * ok: all well
        * warning: an issue has arisen, but the computation can continue.
        * discard: an operation has resulted in invalid output, which must be discarded
        * error: an error has ocurred for this specific FMU instance.
        * fatal: an fatal error has ocurred which has corrupted ALL FMU instances.
        * pending: indicates that the FMu is doing work asynchronously, which can be retrived later.

    Notes:
        FMI section 2.1.3

    """

    ok = 0
    warning = 1
    discard = 2
    error = 3
    fatal = 4
    pending = 5


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
        myModel.fmi2DoStep(ti, dt, False)
        RN[idx] = myModel.RNio

    plt.plot(t, RN)
    plt.ylabel("RN")
    plt.xlabel("t")
    plt.show()