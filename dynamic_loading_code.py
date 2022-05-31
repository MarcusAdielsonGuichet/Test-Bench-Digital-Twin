#Hypothesis that Geometry, Analaysis, SolverCCX, Material, Self Weight, Initial displacement and Mesh are set for the model in the GUI

def dynamic_loading_test(freeCAD_doc_path, dir_name, test_time_length,time_increment, init_disp):

    nb_steps=test_time_length//time_increment
    step_nb=0

    FreeCAD.openDocument(freeCAD_doc_path)
	file_name=os.path.splitext(os.path.basename(freeCAD_doc_path))[0]#extract file name
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
    import FemGui
    FemGui.setActiveAnalysis(doc.Analysis)

    ###
    # run the analysis step by step
    from femtools import ccxtools
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

    ###



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

def create_new_directory(parent,child):
    import os
    # New Path
    path = os.path.join(parent, child)
    # Create the child directory
    try:
        os.makedirs(path, exist_ok = True)
    except OSError as error:
        "Directory '%s' can not be created" % child

def read_frd(Directory_path):
    frd=open(Directory_path, "r")

    return file.txt

def write_step_equation(f, ccxwriter):





def dynamic_loading_test(freeCAD_doc_path, test_time_length,time_increment, init_disp):
    from femtools import ccxtools
    nb_steps=test_time_length//time_increment
    step_nb=0
    # opening the geometry and analysis FreeCAD file
    FreeCAD.openDocument(freeCAD_doc_path)
    file_name=os.path.splitext(os.path.basename(freeCAD_doc_path))[0]
    App.setActiveDocument(file_name)
    App.ActiveDocument=App.getDocument(file_name)
    freeCAD_doc=App.ActiveDocument

    # activating analysis
        import FemGui
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
    else:
        FreeCAD.Console.PrintError("Houston, we have a problem! {}\n".format(message))  # in report view
            print("Houston, we have a problem! {}\n".format(message))  # in python console
        # loop
        while step_nb<=nb_steps :
        new_displacement=Calculate_and_return_new_diplacement(external_file/software)#function to create
        new_step_inp_file=add_step_to_inp_file(new_displacement, previous_inp_file)#function to create, that does the following inp modification
        # run the analysis for each step or create a new analysis for each step?
        fea_step = ccxtools.FemToolsCcx()
        fea_step.update_objects()
        fea_step.setup_working_dir()
        fea_step.setup_ccx()
            message = fea_step.check_prerequisites()
            if not message:
                fea_step.purge_results()
                fea_step.ccx_run()
                fea_step.load_results()
                step_nb+=1
        else:
            FreeCAD.Console.PrintError("Houston, we have a problem! {}\n".format(message))  # in report view
                print("Houston, we have a problem! {}\n".format(message))  # in python console

























