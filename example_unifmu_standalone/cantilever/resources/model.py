import pickle
import os
import sys
import shutil
import glob
import subprocess
import numpy as np
import tempfile


class Model:
    def __init__(self) -> None:

        #Parameters for CCX
        self.first_increment_value = 1e-5
        self.step_duration = 1
        self.min_increment_value = 1e-3
        self.max_increment_value = 1e-1
        self.output_type = "Disp"
        self.disp_value =20
        self.disp_node_set_name ="ConstraintDisplacement"
        self.fixed_node_set_name ="ConstraintFixed"
        self.first_degree_freedom =1
        self.last_degree_freedom =1
        self.nb_steps_prior =0
        self.analysis_type ="Static"
        self.total_steps=20
        self.error=False

        #Directories
        self.ccx_exe_path =r"C:\Users\marcu\OneDrive\Desktop\calculix2.19win64\ccx\ccx_219.exe"
        self.work_dir =r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs"
        self.rout_dir=r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs\Step_1"

        #Outputs
        self.dat_filename=""
        self.mass_matrix=""
        self.stiff_matrix=""
        self.RPio =0.0#need info from Giuseppe; according to the paper, R is the restoring force
        self.Dfbkio =0.0#need info from Giuseppe; according to the paper D = M +C*γ*∆t +K*β*∆t² with M mass matrix, C damping matrix, K stiffness matrix, γ and β are the parameters of the Newmark scheme for the PS (Bathe 1982)?
        self.Ffbkio =0.0#need info from Giuseppe; according to the paper f=M*∆t*a(t)?
        self.Tfbkio =0.0#need info from Giuseppe; Time?


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
            10: "nb_steps_prior",
            11: "ccx_exe_path",
            12: "work_dir",
            13: "analysis_type",
            14: "rout_dir",
            15: "dat_filename",
            16: "mass_matrix",
            17: "stiff_matrix",
            18: "error",
            19: "total_steps"
            20: "RPio"
            21: "Dfbkio"
            22: "Ffbkio"
            23: "Tfbkio"
        }

        #self._update_outputs()

    def fmi2DoStep(self, current_time, step_size, no_step_prior):
        #Use cases:
            #First step without error
            #First step with error(wrong inp name usually)
            #Nth step without error
            #Nth step with error, due to existing dir from previous run, wrong inp, step characteristics not compatible with exp,
        #self.work_dir=tempfile.mkdtemp()
        if self.error==False:
            if self.nb_steps_prior<= self.total_steps-1:

                if self.nb_steps_prior==0:#Checking for the first step
                    #Finding the inp file
                    step_dir=self.rout_dir
                    for root, dirs, files in os.walk(step_dir):
                        for file in files:
                            if file.endswith('.inp'):#hypothesis that there is only one inp file per step directory
                                new_step_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
                                break
                            else:
                                continue
                        break


                elif self.nb_steps_prior>0:#Nth step check
                    new_step_folder_name=f"Step_{self.nb_steps_prior+1}"#Step directory name
                    new_step_name=f"init_Step_{self.nb_steps_prior+1}"#Step inp file name

                    #Necessary procedure for the *RESTART function, check ccx manual for more info
                    step_dir=self.copy_rename_rout_to_rin(new_step_folder_name,new_step_name)

                    #Generate the step inp file
                    self.step_inpfile_writer(step_dir,new_step_name)


                out=self.run_inp_file(step_dir,new_step_name)


                if "Job finished" in out:
                    #self._update_outputs()#need to modify this with the actual outputs
                    self.nb_steps_prior+=1
                    if self.nb_steps_prior< self.total_steps:
                        print(f"\nStep {self.nb_steps_prior} done\nMoving on to Step {self.nb_steps_prior+1}...\n")
                    elif self.nb_steps_prior==self.total_steps:
                        print(f"Step {self.nb_steps_prior} done\n\nSimulation run complete with no errors")
                    return Fmi2Status.ok
                else:
                    self.error=True
                    #Can I do this? Or better to write error function?
                    prin(out)
                    return Fmi2Status.error
            else:
                print("Simulation done")
                return Fmi2Status.ok
        else:
            #weird use case, needs tests first
            return Fmi2Status.error


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
        if self.nb_steps_prior==self.total_steps-1:
            #Terminate simulation?
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
            self.nb_steps_prior,
            self.ccx_exe_path,
            self.work_dir,
            self.rout_dir,
            self.dat_filename,
            self.mass_matrix,
            self.stiff_matrix,
            self.analysis_type,
            self.error
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
            nb_steps_prior,
            ccx_exe_path,
            work_dir,
            rout_dir,
            dat_filename,
            mass_matrix,
            stiff_matrix,
            error,
            analysis_type


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
        self.nb_steps_prior =nb_steps_prior
        self.ccx_exe_path =ccx_exe_path
        self.work_dir =work_dir
        self.analysis_type =analysis_type
        self.rout_dir=rout_dir
        self.dat_filename=dat_filename
        self.mass_matrix=mass_matrix
        self.stiff_matrix=stiff_matrix
        self.error=error

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

        self.RPio =#need info from Giuseppe
        self.Dfbkio =#need info from Giuseppe
        self.Ffbkio =#need info from Giuseppe
        self.Tfbkio =#need info from Giuseppe

    def copy_rename_rout_to_rin(self,new_step_folder_name, new_step_name):
        #self.work_dir=tempfile.mkdtemp()
        # New step folder path
        #print(os.getcwd())
        global rout_file_name
        step_dir = os.path.join(self.work_dir, new_step_folder_name)
        # Create the directory if it doesn't already exist
        try:
            os.mkdir(step_dir)
            for root, dirs, files in os.walk(self.rout_dir):#search inside the dir for the rout file
                for file in files:
                    if file.endswith('.rout'):
                        rout_file_name=file
                        break
                    else:
                        continue
                break
            rout_path = os.path.join(self.rout_dir, rout_file_name)#build the complete path for the rout file
            shutil.copy(rout_path,step_dir) #copy the file to the new folder

            copied_rout_file = os.path.join(step_dir,rout_file_name)#build the new path for the rout file
            new_rin_file_name = os.path.join(step_dir, new_step_name+".rin")#define the new step file name, this name must be the same as the inp file, here new_step_name

            os.rename(copied_rout_file, new_rin_file_name)#rename
            self.rout_dir=step_dir
            return step_dir

        #If it does exist, delete and replace it
        except OSError as error:
            shutil.rmtree(step_dir, ignore_errors=True)
            os.mkdir(step_dir)
            for root, dirs, files in os.walk(self.rout_dir):#search inside the dir for the rout file
                for file in files:
                    if file.endswith('.rout'):
                        rout_file_name=file
                        break
                    else:
                        continue
                break
            rout_path = os.path.join(self.rout_dir, rout_file_name)#build the complete path for the rout file
            shutil.copy(rout_path,step_dir) #copy the file to the new folder

            copied_rout_file = os.path.join(step_dir,rout_file_name)#build the new path for the rout file
            new_rin_file_name = os.path.join(step_dir, new_step_name+".rin")#define the new step file name, this name must be the same as the inp file, here new_step_name

            os.rename(copied_rout_file, new_rin_file_name)#rename
            self.rout_dir=step_dir
            return step_dir


    def step_inpfile_writer(self, step_dir,new_step_name):#needs a previous run, rename the last_step.rout into new_inp_file.rin

        new_inp=open(os.path.join(step_dir, new_step_name+".inp"), 'w')
        #Continuing the previous step calculation
        new_inp.write("*RESTART, READ\n")

        #Step characteristics and analysis type
        new_inp.write("*STEP, INC=1000000\n")
        new_inp.write(f"*{self.analysis_type}\n")
        new_inp.write(f"{self.first_increment_value},{self.step_duration},{self.min_increment_value},{self.max_increment_value}\n")

        #Saving the calculation for next step
        new_inp.write("*RESTART, WRITE\n")

        #Displaced nodes characteristics, add force loads?
        new_inp.write("*BOUNDARY\n")
        new_inp.write(f"{self.disp_node_set_name},{self.first_degree_freedom},{self.last_degree_freedom},{self.disp_value}\n")

        #Fixed nodes
        new_inp.write("*BOUNDARY\n")
        new_inp.write(f"{self.fixed_node_set_name},1,6,0\n")

        #Output files and values
        new_inp.write(f"*NODE PRINT, NSET={self.disp_node_set_name}")
        if self.output_type=="Disp":
            new_inp.write("\nU\n")
        elif self.output_type=="Force":
            new_inp.write(",Totals=Yes\nRF\n")

        new_inp.write("*END STEP\n")

        #Mass and stiffness storage
        new_inp.write("*STEP\n")
        new_inp.write("*FREQUENCY, SOLVER=MATRIXSTORAGE\n")
        new_inp.write("*END STEP")
        new_inp.close()

    def run_inp_file(self,step_dir,new_step_name):
        os.chdir(step_dir)
        output=subprocess.run(
            [self.ccx_exe_path,"-i",new_step_name],
            capture_output=True,
            check=True,
            encoding='utf-8'
        ).stdout
        os.chdir(self.work_dir)
        if "Job finished" not in output:
            self.error=True
        return output

    def get_disp(dat_filename, node_set_name):
        file=open(dat_filename,'r')
        result_disp=[]
        disp_section=False
        for line in file:
            if len(line.split())>1:
                if line.split()[0]=="displacements" and node_set_name in line:
                    disp_section=True
                if line.split()[0].isnumeric()==False and line.split()[0]!="displacements":
                    disp_section=False
                if disp_section==True and line.split()[0].isnumeric():#Verfication for non-blank lines and disp section
                    node_nb,ux,uy,uz=int(line.split()[0]),float(line.split()[1]),float(line.split()[2]),float(line.split()[3])
                    result_disp.append([node_nb,ux,uy,uz])
        file.close()#is this necessary?
        return result_disp

    def get_node_forces(dat_filename,node_set_name):
        file=open(dat_filename,'r')
        result_forces=[]
        node_force_section=False
        for line in file:
            if len(line.split())>1:
                if line.split()[0]=="forces" and node_set_name in line:
                    node_force_section=True
                if line.split()[0].isnumeric()==False and line.split()[0]!="forces":
                    node_force_section=False
                if node_force_section==True and line.split()[0].isnumeric():#Verfication for non-blank lines and disp section
                    node_nb,fx,fy,fz=int(line.split()[0]),float(line.split()[1]),float(line.split()[2]),float(line.split()[3])
                    result_forces.append([node_nb,fx,fy,fz])
        file.close()#is this necessary?
        return result_forces

    def isfloat(num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def get_force_sum(dat_filename,node_set_name):
        file=open(dat_filename,'r')
        forces_section=False
        result_force_sum=[]
        for line in file:
            if len(line.split())>1:
                if "total force" in line and node_set_name in line:
                    forces_section=True
                if isfloat(line.split()[0])==False and "total force" not in line:#works but not as wanted
                    forces_section=False
                if forces_section==True and isfloat(line.split()[0]):#Verfication for non-blank lines and disp section
                    fx,fy,fz=float(line.split()[0]),float(line.split()[1]),float(line.split()[2])
                    result_force_sum.append([fx,fy,fz])
        file.close()#is this necessary?
        return result_force_sum

    def get_mass_matrix(mas_filename):
        file=open(mas_filename,'r')
        result_mat=[]
        for line in file:
            if len(line.split())>1:#filters out the last blank line
                mat_line, mat_column,value=int(line.split()[0]),int(line.split()[1]),float(line.split()[2])
                result_mat.append([mat_line,mat_column,value])

        #Storing the values into a np array? Given that only non-zero values are given by the .mas file, is it important to have the complete matrix?
        n,p= result_mat[len(result_mat)-1][0],result_mat[len(result_mat)-1][1]
        mass_mat=np.zeros((n,p))
        for element in result_mat:
            mass_mat[element[0]-1,element[1]-1]=element[2]

        file.close()#is this necessary?
        return mass_mat

    def get_stiffness_matrix(sti_filename):
        file=open(sti_filename,'r')
        result_mat=[]
        for line in file:
            if len(line.split())>1:
                mat_line, mat_column,value=int(line.split()[0]),int(line.split()[1]),float(line.split()[2])
                result_mat.append([mat_line,mat_column,value])

        #Storing the values into a np array? Given that only non-zero values are given by the .sti file, is it important to have the complete matrix? Besides 4 digits are lost in conversion apparently
        n,p= result_mat[len(result_mat)-1][0],result_mat[len(result_mat)-1][1]
        stif_mat=np.zeros((n,p))
        for element in result_mat:
            stif_mat[element[0]-1,element[1]-1]=element[2]

        file.close()#is this necessary?
        return stif_mat



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
    # import matplotlib.pyplot as plt
    import random

    # create FMU
    fea = Model()

    #Step parameters values
    fea.step_duration = 1.0 # step time [s]
    fea.first_increment_value = 1E-5 # first increment value[s]
    fea.min_increment_value =1E-8 # min increment value[s]
    fea.max_increment_value= 1E-1 # max increment value[s]
    t = np.linspace(0.0, 200, 1) # Time axis.
    u =random.sample(range(-20,20), 20) #displacement array[mm]
    print(f"{u}\n")

    fea.ccx_exe_path=r"C:\Users\marcu\OneDrive\Desktop\calculix2.19win64\ccx\ccx_219.exe"
    fea.work_dir=r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs"
    fea.rout_dir=r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs\Step_1"



    fea.output_type="Disp"
    fea.disp_node_set_name="ConstraintDisplacement"
    fea.fixed_node_set_name="ConstraintFixed"
    fea.analysis_type="Static"
    fea.first_degree_freedom=fea.last_degree_freedom=1 #constraints on the x axis
    fea.nb_steps_prior=0
    fea.total_steps=10

    # output
    #RN = np.zeros(step)

    for no_step_prior in range(fea.total_steps):
        fea.disp_value = u[no_step_prior]
        fea.fmi2DoStep(1,1, no_step_prior)
    # plt.plot(t, RN)
    # plt.ylabel("RN")
    # plt.xlabel("t")
    # plt.show()