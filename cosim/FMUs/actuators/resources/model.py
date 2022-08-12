import pickle
import random
from scipy.optimize import fsolve


class Model:
    def __init__(self) -> None:
        #First actuator pivot point coordinates, directing mostly horizontal displacement[mm]
        self.x1=0
        self.y1=50

        #Second actuator pivot point coordinates, directing mostly vertical displacement [mm]
        self.x2=50
        self.y2=0

        #Actuators resting lengths for respective pivot points [mm]
        self.l1=50
        self.l2=50

        #Beam displacement origin point, aka crosspoint between the two actuators at rest[mm]
        self.xc=0
        self.yc=0


        #External inputs
        self.delta_l1=0 #First actuator length change [mm]
        self.delta_l2=0 #Second actuator length change [mm]

        #Outputs
        self.ux =0 #Initial horizontal beam displacement [mm]
        self.uy =0 #Initial vertical beam displacement [mm]

        self.reference_to_attribute = {
            0: "x1",
            1: "y1",
            2: "x2",
            3: "y2",
            4: "l1",
            5: "l2",
            6: "xc",
            7: "yc",
            8: "delta_l1",
            9: "delta_l2",
            10: "ux",
            11: "uy",
        }

        self._update_outputs()

    def fmi2DoStep(self, current_time, step_size, no_step_prior):
        self.actuators_output()
        self._update_outputs()
        return Fmi2Status.ok

    def fmi2EnterInitializationMode(self):
        print("\nSetting up crosspoint coordinates")
        self.xc, self.yc=  fsolve(self.init_equations, (self.x2,self.y1))
        print(f"Given x1={self.x1} mm, y1={self.y1} mm, x2={self.x2} mm, y2={self.y2} mm, l1={self.l1} mm, l2={self.l2} mm\nxc={self.xc} mm\nyc={self.yc} mm\n")
        return Fmi2Status.ok

    def init_equations(self,tuple):
        """Geometrical equations determining the actuators' resting crosspoint"""
        xc,yc=tuple
        return [(xc-self.x1)**2+(yc-self.y1)**2-self.l1**2,(xc-self.x2)**2+(yc-self.y2)**2-self.l2**2]

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
            self.x1,
            self.y1,
            self.x2,
            self.y2,
            self.l1,
            self.l2,
            self.xc,
            self.yc,
            self.delta_l1,
            self.delta_l2,
            self.ux,
            self.uy,
            )
        )
        return Fmi2Status.ok, bytes

    def fmi2ExtDeserialize(self, bytes) -> int:
        (
            x1,
            y1,
            x2,
            y2,
            l1,
            l2,
            xc,
            yc,
            delta_l1,
            delta_l2,
            ux,
            uy,
        ) = pickle.loads(bytes)
        self.x1 =x1
        self.y1 =y1
        self.x2 =x2
        self.y2 =y2
        self.l1 =l1
        self.l2 =l2
        self.xc =xc
        self.yc =yc
        self.delta_l1 =delta_l1
        self.delta_l2 =delta_l2
        self.ux =ux
        self.uy =uy
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
        return Fmi2Status.ok

    def actuators_output(self):
        """Updates the actuators inputs and prints the new calculated displacements for the cantilever beam"""
        print("Defining random inputs")
        #Random external input from FMU  generator
        new_delta_l1=0
        new_delta_l2=0
        new_delta_l1=random.uniform(self.delta_l1-0.5,self.delta_l1+0.5)
        while new_delta_l1<-5 or new_delta_l1>5:
            new_delta_l1=random.uniform(self.delta_l1-0.5,self.delta_l1+0.5)
        self.delta_l1=new_delta_l1

        new_delta_l2=random.uniform(self.delta_l2-1,self.delta_l2+1)
        while new_delta_l2<-20 or new_delta_l1>20:
            new_delta_l2=random.uniform(self.delta_l2-1,self.delta_l2+1)
        self.delta_l2=new_delta_l2
        print("Random inputs generated, calculating displacements outputs")
        self.ux, self.uy= fsolve(self.step_equations, (self.delta_l1,self.delta_l2))
        print(f"Given delta_l1={self.delta_l1} mm and delta_l2={self.delta_l2} mm\nux={self.ux} mm\nuy={self.uy} mm\n\n")

    def step_equations(self,tuple):
        """Geometrical equations determining the displacements inputs"""
        ux,uy=tuple
        return [(self.xc+ux-self.x1)**2+(self.yc+uy-self.y1)**2-(self.l1+self.delta_l1)**2,(self.xc+ux-self.x2)**2+(self.yc+uy-self.y2)**2-(self.l2+self.delta_l2)**2]


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


if __name__ == "__main__":

    actuators=Model()

    actuators.fmi2EnterInitializationMode()

    for step in range(3):
        print(f"Step {step+1}")
        actuators.fmi2DoStep(1,1, step)
