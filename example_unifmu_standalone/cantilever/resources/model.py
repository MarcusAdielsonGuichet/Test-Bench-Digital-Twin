import pickle
import os
import sys
import shutil
import glob
import subprocess
import numpy as np


class Model:
    def __init__(self) -> None:
        self.first_increment_value = 0.0
        self.step_duration = 0.0
        self.min_increment_value = 0.0
        self.max_increment_value = 0.0
        self.output_type = ""
        self.disp_value =0.0
        self.disp_node_set_name =""
        self.first_degree_freedom =0
        self.last_degree_freedom =0
        self.total_step =0
        self.ccx_exe_path =""
        self.work_dir =""
        self.first_inp_directory =""
        self.rout_filename=""
        self.dat_filename=""
        self.mass_matrix_filename =""
        self.stiff_matrix_filename =""


        self.reference_to_attribute = {
            0: "first_increment_value",
            1: "step_duration",
            2: "min_increment_value",
            3: "max_increment_value",
            4: "output_type",
            5: "disp_value",
            6: "disp_node_set_name",
            7: "fixed_node_set_name",
            8: "first_degree_freedom",
            9: "last_degree_freedom",
            10: "total_steps",
            11: "ccx_exe_path",
            12: "work_dir"
            13: "first_inp_directory"
            14: "rout_filename"
            15: "dat_filename"
            16: "mass_matrix_filename"
            17: "stiff_matrix_filename"
        }

        self._update_outputs()

    def fmi2DoStep(self, current_time, step_size, no_step_prior):
        self._update_outputs()
        # read file from filename
        # do stuff from file
        print(self.filename)
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
                self.real_a,
                self.real_b,
                self.integer_a,
                self.integer_b,
                self.boolean_a,
                self.boolean_b,
                self.string_a,
                self.string_b,
                self.filename
            )
        )
        return Fmi2Status.ok, bytes

    def fmi2ExtDeserialize(self, bytes) -> int:
        (
            real_a,
            real_b,
            integer_a,
            integer_b,
            boolean_a,
            boolean_b,
            string_a,
            string_b,
            filename
        ) = pickle.loads(bytes)
        self.real_a = real_a
        self.real_b = real_b
        self.integer_a = integer_a
        self.integer_b = integer_b
        self.boolean_a = boolean_a
        self.boolean_b = boolean_b
        self.string_a = string_a
        self.string_b = string_b
        self.filename = filename
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
        self.real_c = self.real_a + self.real_b
        self.integer_c = self.integer_a + self.integer_b
        self.boolean_c = self.boolean_a or self.boolean_b
        self.string_c = self.string_a + self.string_b


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
    m = Model()

    assert m.real_a == 0.0
    assert m.real_b == 0.0
    assert m.real_c == 0.0
    assert m.integer_a == 0
    assert m.integer_b == 0
    assert m.integer_c == 0
    assert m.boolean_a == False
    assert m.boolean_b == False
    assert m.boolean_c == False
    assert m.string_a == ""
    assert m.string_b == ""
    assert m.string_c == ""

    m.real_a = 1.0
    m.real_b = 2.0
    m.integer_a = 1
    m.integer_b = 2
    m.boolean_a = True
    m.boolean_b = False
    m.string_a = "Hello "
    m.string_b = "World!"

    assert m.fmi2DoStep(0.0, 1.0, False) == Fmi2Status.ok

    assert m.real_c == 3.0
    assert m.integer_c == 3
    assert m.boolean_c == True
    assert m.string_c == "Hello World!"
