#Hypothesis that Geometry, Analaysis, SolverCCX, Material, Self Weight, Initial displacement and Mesh are set for the model in the GUI
import os
import shutil
import FemGui
import FreeCad
import femtools
from femtools import ccxtools

def create_new_directory(parent,child):
    # New Path
    path = os.path.join(parent, child)
    # Create the child directory
    try:
        os.makedirs(path, exist_ok = True)
    except OSError as error:
        "Directory '%s' can not be created" % child

def dynamic_loading_test(freeCAD_doc_path, test_time_length,time_increment, init_disp):
    nb_steps=test_time_length//time_increment
    step_nb=1
    # opening the geometry and analysis FreeCAD file
    FreeCAD.openDocument(freeCAD_doc_path)
    file_name=os.path.splitext(os.path.basename(freeCAD_doc_path))[0]
    App.setActiveDocument(file_name)#this doesn't work apparently, don't know if it's useful thought
    App.ActiveDocument=App.getDocument(file_name)#same here
    freeCAD_doc=App.ActiveDocument

    # activating analysis
    FemGui.setActiveAnalysis(freeCAD_doc.Analysis)

    # run the analysis step by step for the first one
    fea = ccxtools.FemToolsCcx()
    fea.update_objects()
    fea.setup_working_dir()
    fea.setup_ccx()
    message = fea.check_prerequisites()
    if not message:
        fea.purge_results()
        fea.write_inp_file() #initial displacement
        fea.ccx_run()
        fea.load_results()
	#add a variable that fetch the directory of the tests for the add_step function
    else:
        FreeCAD.Console.PrintError("Houston, we have a problem! {}\n".format(message))  # in report view
            print("Houston, we have a problem! {}\n".format(message))  # in python console
        # loop
    while step_nb<=nb_steps :
        step_nb+=1
	previous_resulting_displacement=find_diplacement(external_file/software)#function to create
	#add input for new displacement/text window to modify the values of the displacement
	#Open Gui window for the displacement
	#Ask user to input new values and confirm once done
	#Continue running the code
	new_displacement=input_from_user()
        new_step_inp_file=add_step_to_inp_file(analysis_directory, freeCAD_doc, previous_inp_file)#function to create, that does the following inp modification
        # run the analysis for each step or create a new analysis for each step?
        fea_step = ccxtools.FemToolsCcx()
        fea_step.update_objects()
        fea_step.setup_working_dir()#might need to modifiy this for a more explicit directory and taking the new inp files
        fea_step.setup_ccx()
        message = fea_step.check_prerequisites()
	if not message:
		fea_step.purge_results()
		fea_step.ccx_run()
		fea_step.load_results()
        else:
            FreeCAD.Console.PrintError("Houston, we have a problem! {}\n".format(message))  # in report view
                print("Houston, we have a problem! {}\n".format(message))  # in python console

#Not finished
def find_diplacement(frd_file):#careful with hexa20 mesh elements, node order is different in inp and frd
	#inspiration from the read_frd_result() line 555 FreeCAD/importCcxFrdResults.py at 8041f0c032edad1c268bd7cc0f0c4921a5814e94 · FreeCAD/FreeCAD · GitHub
	for line in frd_file:
		if line[5:9] == "DISP":
		    mode_disp_found = True
		if mode_disp_found and (line[1:3] == "-1"):
		    # we found a displacement line
		    elem = int(line[4:13])
		    mode_disp_x = float(line[13:25])
		    mode_disp_y = float(line[25:37])
		    mode_disp_z = float(line[37:49])
		    mode_disp[elem] = FreeCAD.Vector(mode_disp_x, mode_disp_y, mode_disp_z)
		 # Check if we found the end of a section
        	if line[1:3] == "-3":
            		end_of_section_found = True
		            if mode_disp_found:
				mode_results["disp"] = mode_disp
				mode_disp = {}
				mode_disp_found = False
				node_element_section = False
	return displacement


from FreeCAD import write_constraint_displacement as con_displacement
from FreeCAD import write_constraint_fixed as con_fixed

#Almost finished
def add_step_to_inp_file(directory, doc, step_nb):
    dir_path = directory
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.inp'):
                previous_inp_file_path=root+'/'+str(file)
                new_inp_file_path=root+'/'+os.path.splitext(os.path.basename(file))[0]+" Step "+str(step_nb)+".inp"
    shutil.copy(previous_inp_file_path,new_inp_file_path)
    #code above works 01/06/2022 18:00, needs r+directory if '\' are used
	
	new_inp_file=open(new_inp_file_path, 'a+')
	for line in new_inp_file:
		if "*END STEP" in line:
			end_step_count+=1
		if end_step_count==nb-1:
			write_dynamic_step(new_inp_file)# write the dynamic calcultation line
			
			cons_fixed=femtools.membertools.get_member(doc.Analysis,"Fem::ConstraintFixed")
			write_constraints_propdata(inpfile, doc.ConstraintFixed, con_fixed)#writes the comment on the inp file as well as the fixed constraints
			#*********************************************************** f.write("\n{}\n".format(59 * "*"))
			#** Fixed Constraints by get_constraint_title function
			#** written by write_constraints_fixed function
			#** ConstraintFixed by the for loop inside write_constraints_propdata, dependent on the number of displacements in the analysis group, writes their label
			#*BOUNDARY by write_constraint function 
			#ConstraintFixed,1 Fixed in X direction
			#ConstraintFixed,2 Fixed in Y direction
			#ConstraintFixed,3 Fixed in Z direction
			
			cons_displacement=femtools.membertools.get_member(doc.Analysis,"Fem::ConstraintDisplacement")	
			write_constraints_propdata(inpfile, cons_displacement, con_displacement)#writes the comment on the inp file
			#*********************************************************** f.write("\n{}\n".format(59 * "*"))
			#** Displacement constraint applied by get_constraint_title function
			#** written by write_constraints_displacement function 
			#** ConstraintDisplacement (label of the displacement in FreeCAD) by the for loop inside write_constraints_propdata, dependent on the number of displacements in the analysis group, writes their label
			#*BOUNDARY
			#ConstraintDisplacement,Degree of freedom, Degree of freedom, Displacement Value

			
			# output and step end
			write_step_output.write_step_output(inpfile)#informs CCX on the type of data to be written in the frd output file
			write_step_equation.write_step_end(inpfile)#writes the step end line
#Maybe finished	
def write_dynamic_step(file):
	file.write("*STEP\n")
	file.write("*MODAL DYNAMIC, PERTUBATION\n")
	#Add time increment and step time value?

	
#in write_constraints_propdata():femtools.membertools.get_member(doc.Analysis,"Fem::ConstraintDisplacement")(I think) =all Fem::ConstraintDisplacement objects in analysis=member.cons_displacement=femobjs	
#so write_constraints_propdata(inpfile, member.cons_fixed, con_fixed)	
	
##Draft codes	

def dynamic_loading_test_draft(freeCAD_doc_path, dir_name, test_time_length,time_increment, init_disp):

    nb_steps=test_time_length//time_increment
    step_nb=0

    FreeCAD.openDocument(freeCAD_doc_path)
	file_name=os.path.splitext(os.path.basename(freeCAD_doc_path))[0] #extract file name
	App.setActiveDocument(file_name)
	App.ActiveDocument=App.getDocument(file_name)
    freeCAD_doc=App.ActiveDocument
    # Gui.ActiveDocument=Gui.getDocument("Test_Frame")

    # displaced_face=freeCAD_doc.displaced_face
    # fixed_face=freeCAD_doc.fixed_face
    #


    # import to create objects
    # import ObjectsFem
    #
    # analysis
    # analysis_object = ObjectsFem.makeAnalysis(freeCAD_doc, "Analysis")
    #
    # solver (we gone use the well tested CcxTools solver object)
    # solver_object = ObjectsFem.makeSolverCalculixCcxTools(freeCAD_doc, "CalculiX")
    # solver_object.GeometricalNonlinearity = 'linear'
    # solver_object.ThermoMechSteadyState = Dynamic
    # solver_object.MatrixSolverType = 'default'
    # solver_object.IterationsControlParameterTimeUse = False
    # analysis_object.addObject(solver_object)
    #
    # material
    # material_object = ObjectsFem.makeMaterialSolid(freeCAD_doc, "SolidMaterial")
    # mat = material_object.Material
    # mat['Name'] = "Steel-Generic"
    # mat['YoungsModulus'] = "210000 MPa"
    # mat['PoissonRatio'] = "0.30"
    # mat['Density'] = "7900 kg/m^3"
    # material_object.Material = mat
    # analysis_object.addObject(material_object)
    #
    # Sets the Fixed Constraints on the model
    # model_constraints=freeCAD_doc.fem.Constraints()
    # fixed_constraint
    # fixed_constraint = ObjectsFem.makeConstraintFixed(freeCAD_doc, "FemConstraintFixed")
    # fixed_constraint.References = [(freeCAD_doc, fixed_face)]
    # analysis_object.addObject(fixed_constraint)
    #
    #
    # initial_displacement_constraint
    # displacement_face=input("Select displacement element")
    # displacement_constraint = ObjectsFem.makeConstraintDisplacement(freeCAD_doc, name="FemConstraintDisplacement")
    # displacement_constraint.References = [(freeCAD_doc, displaced_face)]
    #
    # displacement_constraint.xFix = False
    # displacement_constraint.xFree = False
    # displacement_constraint.xDisplacement =init_disp[0]
    #
    # displacement_constraint.yFix = False
    # displacement_constraint.yFree = False
    # displacement_constraint.yDisplacement =init_disp[1]
    #
    # displacement_constraint.zFix = False
    # displacement_constraint.zFree = False
    # displacement_constraint.zDisplacement =[2]
    #
    # analysis_object.addObject(displacement_constraint)
    # activating analysis
    FemGui.setActiveAnalysis(doc.Analysis)

    ###
    # run the analysis step by step
    fea = ccxtools.FemToolsCcx()
    fea.update_objects()
    fea.setup_working_dir()
    fea.setup_ccx()
    message = fea.check_prerequisites()
    if not message:
        fea.purge_results()
        # fea.write_inp_file()

        # on error at inp file writing, the inp file path "" was returned (even if the file was written)
        # if we would write the inp file anyway, we need to again set it manually
        # fea.inp_file_name = '/tmp/FEMWB/FEMMeshGmsh.inp'
        fea.ccx_run()
        fea.load_results()
    else:
        FreeCAD.Console.PrintError("Houston, we have a problem! {}\n".format(message))  # in report view
        print("Houston, we have a problem! {}\n".format(message))  # in python console
    while step_nb<=nb_steps:
        test_path="Test_"+str(step_nb)
        #Add a new working folder for each step(containing INP,FRD, DAT...files)
        create_new_directory(dir_name,test_path)
        #Initial step
        if step_number=0:
            disp_input=set_disp(freeCAD_doc, init_disp)
            init_mesh=freeCAD_doc.fem.mesh_model()

        else:
            sim_disp_response_file=calc_resp_disp(result_file)
            sim_resp_disp=getdisp(sim_disp_response_file)
            disp_input=set_disp(freeCAD_doc, sim_resp_disp)
            new_mesh=init_mesh+displacement

        input_file= fea.write_inp file(model_constraints,displacement_input, mesh)
        fea.ccx_run_dynamics()
        result_file=test_path_frd_file
    print("Dynamic test sucessful")	
	
#Useless, just need to change the displacement value in the next step, no need to get the nodes in the node set
				#def find_displacement_node_set(inp_file):
#	for line in inp_file:
#		if "ConstraintDisplacement" in line:
#			node_set=True
#		if node_set=True and 
	#get_constraints_displacement_nodes()
# src contains the path of the source file
	#src=previous_inp_file_path
	# dest contains the path of the destination file
	#dest =directory
	# using copy2()
	#new_inp_path=shutil.copy2(src,dest)
				
	
	# src contains the path of the source file
	#src=previous_inp_file_path
	# dest contains the path of the destination file
	#dest =directory
	# using copy2()
	#new_inp_path=shutil.copy2(src,dest)














