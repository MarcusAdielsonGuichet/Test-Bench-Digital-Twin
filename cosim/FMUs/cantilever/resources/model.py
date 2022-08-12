import pickle
import os
import sys
import shutil
import glob
import subprocess
import numpy as np
import tempfile
import random



class Model:
    def __init__(self) -> None:

        #Directories
        self.ccx_exe_path=r"C:\Users\marcu\OneDrive\Desktop\calculix2.19win64\ccx\ccx_219.exe"#only need path env variable? or use a path finder based on the current file
        self.work_dir=r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs"#work on a temp dir
        self.rout_dir=r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs\Step_1"#copy and paste in temp dir

        #Status checks
        self.nb_steps_prior=0
        self.total_steps=20
        self.error=False #Need to replace with the Fmistatus class?

        #Internal inputs
        #Parameters for CCX
        #Time parameters [s]
        self.first_increment_value = 1e-5
        self.step_duration = 1
        self.min_increment_value = 1e-3
        self.max_increment_value = 1e-1

        self.disp_node_set_name ="ConstraintDisplacement"
        self.fixed_node_set_name ="ConstraintFixed"
        self.analysis_type ="Static"
        self.output_type ="Force"


        #Geometrical caracteristics
        self.L =600 #Length of cantilever beam [mm]

        #External inputs
        self.ux =0 #Initial horizontal beam displacement [mm]
        self.uy =0 #Initial vertical beam displacement [mm]

        #Outputs
        self.Fxbo=0.0 #Resulting horizontal force beam-->actuator[N]
        self.Fybo=0.0 #Resulting vertical force beam-->actuator[N]
        self.Fxfo=0.0 #Resulting horizontal force beam-->frame[N]
        self.Fyfo=0.0 #Resulting vertical force beam-->frame[N]
        self.Mzfo=0.0 #Resulting z axis torque beam-->frame[N.m]

        self.dat="" #Displacement and force output filename
        self.mass_mat="" #Mass matrix output filename
        self.stiff_mat="" #Stiffness matrix output filename


        self.reference_to_attribute = {
            0: "ccx_exe_path",
            1: "work_dir",
            2: "rout_dir",
            3: "nb_steps_prior",
            4: "total_steps",
            5: "error",
            6: "first_increment_value",
            7: "step_duration",
            8: "min_increment_value",
            9: "max_increment_value",
            10: "disp_node_set_name",
            11: "fixed_node_set_name",
            12: "analysis_type",
            13: "output_type",
            14: "L",
            15: "ux",
            16: "uy",
            17: "Fxbo",
            18: "Fybo",
            19: "Fxfo",
            20: "Fyfo",
            21: "Mzfo",
            22: "dat",
            23: "mass_mat",
            24: "stiff_mat"
        }
        #self._update_outputs()

    def fmi2DoStep(self, current_time, step_size, no_step_prior):
        #Use cases:
            #First step without error
            #First step with error(wrong inp name usually)
            #Nth step without error
            #Nth step with error, due to existing dir from previous run, wrong inp, step characteristics not compatible with exp,
            new_step_folder_name=f"Step_{self.nb_steps_prior+1}"#Step directory name
            new_step_name=f"init_Step_{self.nb_steps_prior+1}"#Step inp file name
            print(f"Step {self.nb_steps_prior+1}...\n")

            #Necessary procedure for the *RESTART function, check ccx manual for more info
            step_dir=self.copy_rename_rout_to_rin(new_step_folder_name,new_step_name)

            #Update inputs
            print("Setting inputs...")
            #self.update_inputs()

            #Generate the step inp file
            self.step_inpfile_writer(step_dir,new_step_name)

            print("\nBeginning step calculations...")
            out=self.run_inp_file(step_dir,new_step_name)
            print("CCX run complete, checking for errors...")

            if "Job finished" in out:
                print("\nNo errors, updating variables...")
                self.dat=os.path.join(step_dir, new_step_name+".dat")
                self._update_outputs()
                self.nb_steps_prior+=1
                print(f"Done\n\n")
                return Fmi2Status.ok
            else:
                return Fmi2Status.error

    def fmi2EnterInitializationMode(self):

        print("\nSetting first inputs...\n")
        #self.update_inputs()

        print("\nStep 1...\nSearching for first inp file")
        new_step_name=""
        #Finding the inp file
        step_dir=self.rout_dir
        for root, dirs, files in os.walk(step_dir):
            for file in files:
                if file.endswith('.inp'):#hypothesis that there is at least and only one inp file per step directory
                    new_step_name=os.path.splitext(os.path.basename(file))[0] #ccx only needs the filename, not the extension
                    print("Inp file found, moving to calculations")
                    break
                else:
                    continue
            break

        #Modifying the first inp file
        new_inp=open(os.path.join(step_dir, new_step_name+".inp"), 'r+')
        step_line_number=0
        lines=new_inp.readlines()
        new_inp.seek(0)
        new_inp.truncate()
        for line_nb,line in enumerate(lines):
            if "*STEP" in line:
                step_line_number=line_nb
                break
        new_inp.writelines(lines[:step_line_number])
        #Step characteristics and analysis type
        new_inp.write("*STEP, INC=1000000\n")
        new_inp.write(f"*{self.analysis_type}\n")
        new_inp.write(f"{self.first_increment_value},{self.step_duration},{self.min_increment_value},{self.max_increment_value}\n")

        #Saving the calculation for next step
        new_inp.write("*RESTART, WRITE\n")

        #Displaced nodes characteristics, add force loads?
        if self.ux!=0:
            new_inp.write("*BOUNDARY\n")
            new_inp.write(f"{self.disp_node_set_name},1,1,{self.ux}\n")
        if self.uy!=0:
            new_inp.write("*BOUNDARY\n")
            new_inp.write(f"{self.disp_node_set_name},3,3,{self.uy}\n")

        #Fixed nodes
        new_inp.write("*BOUNDARY\n")
        new_inp.write(f"{self.fixed_node_set_name},1,3,0\n")

        #Output files and values
        new_inp.write("*NODE FILE\nU\n")
        new_inp.write(f"*NODE PRINT, NSET={self.disp_node_set_name}")
        if self.output_type=="Disp":
            new_inp.write("\nU\n")
        elif self.output_type=="Force":
            new_inp.write(",Totals=Only\nRF\n")

        new_inp.write(f"*NODE PRINT, NSET={self.fixed_node_set_name},Totals=Only\nRF\n")

        new_inp.write("*END STEP\n")

        # #Mass and stiffness matrices storage
        # new_inp.write("*STEP\n")
        # new_inp.write("*FREQUENCY, SOLVER=MATRIXSTORAGE\n")
        # new_inp.write("*END STEP")
        new_inp.close()

        print("Beginning step calculations...")
        out=self.run_inp_file(step_dir,new_step_name)

        if "Job finished" in out:
            print("No errors, updating output variables...")
            self.dat=os.path.join(step_dir, new_step_name+".dat")
            self._update_outputs()
            self.nb_steps_prior+=1
            print(f"Done\n\n")
            return Fmi2Status.ok
        else:
            return Fmi2Status.error

    def fmi2ExitInitializationMode(self):
        #self._update_outputs()
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
            self.ccx_exe_path,
            self.work_dir,
            self.rout_dir,
            self.nb_steps_prior,
            self.total_steps,
            self.error,
            self.first_increment_value,
            self.step_duration,
            self.min_increment_value,
            self.max_increment_value,
            self.disp_node_set_name,
            self.fixed_node_set_name,
            self.analysis_type,
            self.output_type,
            self.L,
            self.ux,
            self.uy,
            self.Fxbo,
            self.Fybo,
            self.Fxfo,
            self.Fyfo,
            self.Mzfo,
            self.dat,
            self.mass_mat,
            self.stiff_mat
            )
        )
        return Fmi2Status.ok, bytes

    def fmi2ExtDeserialize(self, bytes) -> int:
        (
            ccx_exe_path,
            work_dir,
            rout_dir,
            nb_steps_prior,
            total_steps,
            error,
            first_increment_value,
            step_duration,
            min_increment_value,
            max_increment_value,
            disp_node_set_name,
            fixed_node_set_name,
            analysis_type,
            output_type,
            L,
            ux,
            uy,
            Fxbo,
            Fybo,
            Fxfo,
            Fyfo,
            Mzfo,
            dat,
            mass_mat,
            stiff_mat


        ) = pickle.loads(bytes)

        self.ccx_exe_path=ccx_exe_path
        self.work_dir=work_dir
        self.rout_dir=rout_dir
        self.nb_steps_prior=nb_steps_prior
        self.total_steps=total_steps
        self.error=error
        self.first_increment_value=first_increment_value
        self.step_duration=step_duration
        self.min_increment_value =min_increment_value
        self.max_increment_value =max_increment_value
        self.disp_node_set_name =disp_node_set_name
        self.fixed_node_set_name =fixed_node_set_name
        self.analysis_type =analysis_type
        self.output_type =output_type
        self.L =L
        self.ux =ux
        self.uy =uy
        self.Fxbo= Fxbo
        self.Fybo =Fybo
        self.Fxfo =Fxfo
        self.Fyfo =Fyfo
        self.Mzfo =Mzfo
        self.dat =dat
        self.mass_mat= mass_mat
        self.stiff_mat=stiff_mat

        #self._update_outputs()

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

    def update_inputs(self):
        new_ux=random.uniform(self.ux-0.5,self.ux+0.5)
        while new_ux<-5 or new_ux>5:
            new_ux=random.uniform(self.ux-0.5,self.ux+0.5)
        self.ux=new_ux
        sciformat_ux="{:.3e}".format(self.ux)
        print(f"ux={sciformat_ux} mm")

        uy=random.uniform(self.uy-1,self.uy+1)
        while uy<-20 or new_ux>20:
            uy=random.uniform(self.uy-1,self.uy+1)
        self.uy=uy
        sciformat_uy="{:.3e}".format(self.uy)
        print(f"uy={sciformat_ux} mm")

    def _update_outputs(self):
        self.Fxbo=-self.get_force_sum(self.dat, self.disp_node_set_name)[0]
        sciformat_Fxbo="{:.3e}".format(self.Fxbo)
        print(f"FXbo={sciformat_Fxbo} N")

        self.Fybo=-self.get_force_sum(self.dat, self.disp_node_set_name)[2]
        sciformat_Fybo="{:.3e}".format(self.Fybo)
        print(f"FXbo={sciformat_Fybo} N")

        self.Fxfo=-self.Fxbo
        sciformat_Fxfo="{:.3e}".format(self.Fxfo)
        print(f"FXbo={sciformat_Fxfo} N")

        self.Fyfo=-self.Fybo
        sciformat_Fyfo="{:.3e}".format(self.Fyfo)
        print(f"FXbo={sciformat_Fyfo} N")

        self.Mzfo=self.Fybo*self.L*1e-3
        sciformat_Mzfo="{:.3e}".format(self.Mzfo)
        print(f"FXbo={sciformat_Mzfo} N.m")

        return Fmi2Status.ok

    def copy_rename_rout_to_rin(self,new_step_folder_name, new_step_name):
        """Copies a previous run .rout file to a newly-created step folder directory, renaming it as new_step_name.rin.
        This procedure is mandatory for non-continuous multi-steps analyses.
        Check *RESTART keyword on CCX Crunchix manual for more information.
        https://www.openaircraft.com/ccx-doc/ccx/node319.html"""
        rout_file_name=""
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

            os.rename(copied_rout_file, new_rin_file_name)#rename the copied .rout file to the new_step_name.rin
            self.rout_dir=step_dir
            return step_dir


    def step_inpfile_writer(self, step_dir,new_step_name):#needs a previous run, rename the last_step.rout into new_inp_file.rin
        """Creates and writes the inp for the step, according to the CCX manual keywords.
        Requires a previous step to have been calculated, in order for the *RESTART, READ function to work in CCX.

        For this FMU/experiment, only one node set is defined for displacement values, on the x and z defined in the FreeCAD model.
        The analysis is static and returns the total forces exerted on the  displaced node set, as the fixed node set.
        Matrix storage is in comments, if further studies requires it
        More info on how to build the inp file: https://www.openaircraft.com/ccx-doc/ccx/ccx.html"""

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
        if self.ux!=0:
            new_inp.write("*BOUNDARY\n")
            new_inp.write(f"{self.disp_node_set_name},1,1,{self.ux}\n")
        if self.uy!=0:
            new_inp.write("*BOUNDARY\n")
            new_inp.write(f"{self.disp_node_set_name},3,3,{self.uy}\n")

        #Fixed nodes
        new_inp.write("*BOUNDARY\n")
        new_inp.write(f"{self.fixed_node_set_name},1,3,0\n")

        #Output files and values
        new_inp.write("*NODE FILE\nU\n")
        new_inp.write(f"*NODE PRINT, NSET={self.disp_node_set_name}")
        if self.output_type=="Disp":
            new_inp.write("\nU\n")
        elif self.output_type=="Force":
            new_inp.write(",Totals=Only\nRF\n")

        new_inp.write(f"*NODE PRINT, NSET={self.fixed_node_set_name},Totals=Only\nRF\n")

        new_inp.write("*END STEP\n")

        # #Mass and stiffness matrices storage
        # new_inp.write("*STEP\n")
        # new_inp.write("*FREQUENCY, SOLVER=MATRIXSTORAGE\n")
        # new_inp.write("*END STEP")
        new_inp.close()

    def run_inp_file(self,step_dir:str,new_step_name:str)->str:
        """Uses the subprocess.run python function to run CCX on the inp file.
        Returns the output console lines generated by CCX."""
        os.chdir(step_dir)
        output=subprocess.run(
            [self.ccx_exe_path,"-i", new_step_name],
            capture_output=True,
            check=True,
            encoding='utf-8'
        ).stdout
        os.chdir(self.work_dir)#This line is necessary to liberate the last folder for deletion, else python and ccx keep the folder active, making it impossible to delete it
        return output

    def get_disp(self, dat_filename, node_set_name):
        """Reads the dat output file, and return an array containing the node set number and subsequent displacement values"""
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
        file.close()#this is necessary if not using the "with" method
        return result_disp

    def get_node_forces(self, dat_filename,node_set_name):
        """Reads the dat output file, and return an array containing the node set number and subsequent external forces values"""
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
        file.close()#this is necessary if not using the "with" method
        return result_forces

    def get_force_sum(self, dat_filename,node_set_name):
        """Reads the dat output file, and return an array containing the node set number and subsequent external forces values"""
        file=open(dat_filename,'r')
        forces_section=False
        #result_force_sum=[]
        for line in file:
            if len(line.split())>1:
                if "total force" in line and node_set_name.upper() in line:
                    forces_section=True
                if self.isfloat(line.split()[0])==False and "total force" not in line:#works but not as wanted
                    forces_section=False
                if forces_section==True and self.isfloat(line.split()[0]):#Verfication for non-blank lines and disp section
                    fx,fy,fz=float(line.split()[0]),float(line.split()[1]),float(line.split()[2])
                    #result_force_sum.append([fx,fy,fz])
        file.close()#this is necessary if not using the "with" method
        return fx,fy,fz

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

        file.close()#this is necessary if not using the "with" method
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

        file.close()#this is necessary if not using the "with" method
        return stif_mat

    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False



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

    # create FMU
    fea = Model()

    #Step parameters values
    fea.step_duration = 1.0 # step time [s]
    fea.first_increment_value = 1E-5 # first increment value[s]
    fea.min_increment_value =1E-8 # min increment value[s]
    fea.max_increment_value= 1E-1 # max increment value[s]
    fea.total_steps=3

    fea.ccx_exe_path=r"C:\Users\marcu\OneDrive\Desktop\calculix2.19win64\ccx\ccx_219.exe"
    fea.work_dir=r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs"
    fea.rout_dir=r"C:\internship_github\Python-code-for-Test-Bench-Digital-Twin\CCX Files\test_runs\Step_1"

    fea.output_type="Force"
    fea.disp_node_set_name="ConstraintDisplacement"
    fea.fixed_node_set_name="ConstraintFixed"
    fea.analysis_type="Static"

    fea.fmi2EnterInitializationMode()

    for step in range(fea.total_steps):
        fea.fmi2DoStep(1,1, step)