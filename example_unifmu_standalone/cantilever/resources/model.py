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
        self.fixed_node_set_name =""
        self.first_degree_freedom =0
        self.last_degree_freedom =0
        self.total_steps =0
        self.ccx_exe_path =""
        self.work_dir =""
        self.first_inp_directory =""
        self.rout_dir=""
        self.dat_filename=""
        self.mass_matrix_filename =""
        self.stiff_matrix_filename =""
        self.error=False


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
            12: "work_dir",
            13: "first_inp_directory",
            14: "rout_dir",
            15: "dat_filename",
            16: "mass_matrix_filename",
            17: "stiff_matrix_filename",
            18: "error"
        }

        self._update_outputs()

    def fmi2DoStep(self, no_step_prior):
        #3 use cases:
            #First step, so no need for the rout/rin function
            #Nth step without error
            #Nth step with error
        if self.error==False:
            if no_step_prior==0:
                #Finding the inp file
                for root, dirs, files in os.walk(first_inp_directory):
                    for file in files:
                        if file.endswith('.inp'):#hypothesis that there is only one inp file per step directory
                            new_step_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
                            # inp_file_path=os.path.join(first_inp_directory,file)
                            break
                        else:
                            continue
                    break
                step_dir=self.first_inp_directory

            elif no_step_prior>0:
                new_step_folder_name=f"Step_{no_step_prior+1}"
                new_step_name=f"init_Step_{no_step_prior+1}"

                #Necessary procedure for the *RESTART function, check ccx manual for more info
                step_dir=copy_rename_rout_to_rin(self.work_dir,
                rout_file_dir,
                new_step_folder_name,
                new_step_name)

                #Generate and run the new step inp
                new_step_inpfile_writer(step_dir,
                self.first_increment_value,
                self.step_duration,
                self.min_increment_value,
                self.max_increment_value,
                new_step_name,
                self.output_type)

            out=run_inp_file(self.ccx_exe_path,
            step_dir,
            new_step_name)
            if "Job finished" in out:
                self._update_outputs()#need to modify this with the actual outputs
                return Fmi2Status.ok
            else:
                self.error=True
                #Can I do this? Or better to write error function?
                return Fmi2Status.error, out
        else:
            #weird use case, needs tests first
            return Fmi2Status.error

    def copy_rename_rout_to_rin(work_dir,rout_file_dir,new_step_folder_name, new_step_name):
        # New step folder path
        new_path = os.path.join(work_dir, new_step_folder_name)

        # Create the directory if it doesn't already exist
        try:
            os.mkdir(new_path)
            for root, dirs, files in os.walk(rout_file_dir):#search inside the dir for the rout file
                for file in files:
                    if file.endswith('.rout'):
                        rout_file_name=file
                        break
                    else:
                        continue
                break
            rout_path = os.path.join(rout_file_dir, rout_file_name)#build the complete path for the rout file
            shutil.copy(rout_path,new_path) #copy the file to the new folder

            copied_rout_file = os.path.join(new_path,rout_file_name)#build the new path for the rout file
            new_rin_file_name = os.path.join(new_path, new_step_name+".rin")#define the new step file name, this name must be the same as the inp file, here new_step_name

            os.rename(copied_rout_file, new_rin_file_name)#rename
            return new_path
        except OSError as error:
            Fmi2Status.error
            print(error)


    def new_step_inpfile_writer(step_dir,first_increment_value,step_duration,min_increment_value,max_increment_value,new_step_name,output_type):#needs a previous run, rename the last_step.rout into new_inp_file.rin

        new_inp=open(os.path.join(step_dir, new_step_name+".inp"), 'w')
        #Continuing the previous step calculation
        new_inp.write("*RESTART, READ\n")

        #Step characteristics and analysis type
        new_inp.write("*STEP, INC=1000000\n")
        new_inp.write("*STATIC\n")
        new_inp.write(f"{first_increment_value},{step_duration},{min_increment_value},{max_increment_value}\n")

        #Saving the calculation for next step
        new_inp.write("*RESTART, WRITE\n")

        #Displaced nodes characteristics, add force loads?
        new_inp.write("*BOUNDARY\n")
        new_inp.write(f"{disp_node_set_name},{first_degree_freedom},{last_degree_freedom},{disp_value}\n")

        #Fixed nodes
        new_inp.write("*BOUNDARY\n")
        new_inp.write(f"{fixed_node_set_name},1,6,0\n")

        #Output files and values
        new_inp.write(f"*NODE PRINT, NSET={disp_node_set_name}")
        if output_type=="Disp":
            new_inp.write("\nU\n")
        elif output_type=="Force":
            new_inp.write(",Totals=Only\nRF\n")

        new_inp.write("*END STEP\n")

        #Mass and stiffness storage
        new_inp.write("*STEP\n")
        new_inp.write("*FREQUENCY, SOLVER=MATRIXSTORAGE\n")
        new_inp.write("*END STEP")
        new_inp.close()

    def run_inp_file(ccx_exe_path,step_dir,new_step_name):
        os.chdir(step_dir)
        output=subprocess.run(
            [ccx_exe_path,"-i",new_step_name],
            capture_output=True,
            check=True,
            encoding='utf-8'
        ).stdout
        calculation_end="Job finished"
        if calculation_end not in output:
            error=True
        return output

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
            self.first_increment_value,
            self.step_duration,
            self.min_increment_value,
            self.max_increment_value,
            self.output_type,
            self.disp_value,
            self.disp_node_set_name,
            self.fixed_node_set_name,
            self.last_degree_freedom,
            self.total_steps,
            self.ccx_exe_path,
            self.work_dir,
            self.rout_dir,
            self.dat_filename,
            self.mass_matrix_filename,
            self.stiff_matrix_filename
            )
        )
        return Fmi2Status.ok, bytes

    def fmi2ExtDeserialize(self, bytes) -> int:
        (
            first_increment_value,
            step_duration,
            min_increment_value,
            max_increment_value,
            output_type,
            disp_value,
            disp_node_set_name,
            fixed_node_set_name,
            last_degree_freedom,
            total_steps,
            ccx_exe_path,
            work_dir,
            rout_dir,
            dat_filename,
            mass_matrix_filename,
            stiff_matrix_filename

        ) = pickle.loads(bytes)

        self.first_increment_value =first_increment_value
        self.step_duration =step_duration
        self.min_increment_value =min_increment_value
        self.max_increment_value =max_increment_value
        self.output_type =output_type
        self.disp_value =disp_value
        self.disp_node_set_name =disp_node_set_name
        self.fixed_node_set_name =fixed_node_set_name
        self.first_degree_freedom =first_degree_freedom
        self.last_degree_freedom =last_degree_freedom
        self.total_steps =total_steps
        self.ccx_exe_path =ccx_exe_path
        self.work_dir =work_dir
        self.first_inp_directory =first_inp_directory
        self.rout_dir=rout_dir
        self.dat_filename=dat_filename
        self.mass_matrix_filename =mass_matrix_filename
        self.stiff_matrix_filename =stiff_matrix_filename

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
        #modify to satisfy the present problem, the cantilever beam
        #Outputs:
            #Displacement forces
            #Displacement vectors
            #Mass matrix
            #Stiffness matrix

        self.mass_matrix_filename =""
        self.stiff_matrix_filename =""
        self.dat_filename =""
        self.rout_filename =""


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
