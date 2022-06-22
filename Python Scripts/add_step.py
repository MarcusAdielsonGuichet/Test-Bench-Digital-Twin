def add_step(inp_file):
	previous_inp=open(inp_file, 'r')
	new_inp=open("new_inp_file.inp", 'w')
	for line in previous_inp:
		if "*END STEP" in line:
			end_step_count+=1
			if end_step_count==nb-1:
				new_inp.write("*STEP, INC=1000000\n")
				new_inp.write("*DYNAMIC\n")
				new_inp.write(str(first_increment_value)+","+str(step_duration)+","+str(min_increment_value)+","+str(max_increment_value)+"\n")
				#Displaced nodes
				new_inp.write("*BOUNDARY\n")
				new_inp.write("ConstraintDisplacement,"+str(first_degree_freedom)+","+str(last_degree_freedom)+","+str(disp_value)+"\n")
		
				#Fixed nodes
				new_inp.write("*BOUNDARY\n")
				new_inp.write("ConstraintDisplacement,1,6,0\n")

				#Output
				new_inp.write("*NODE PRINT, NSET=ConstraintDisplacement\n")
				new_inp.write("U")
				new_inp.write("*END STEP")
		new_inp.write(line)
	new_inp.close()
	previous_inp.close()

def write_new_step_inpfile_with_restart_read_write(last_step_rout_path,output_type):#needs a previous run, rename the last_step.rout into new_inp_file.rin 
	
	#Renaming the previous step rout into the rin for the next step, as part of the 
	os.rename(last_step_rout_path,'new_inp_file.rin')
	
	new_inp=open("new_inp_file.inp", 'w')
	#Continuing the previous step calculation
	new_inp.write("*RESTART, READ\n")
	
	#Step characteristics and analysis type
	new_inp.write("*STEP, INC=1000000\n")
	new_inp.write("*DYNAMIC\n")
	new_inp.write(str(first_increment_value)+","+str(step_duration)+","+str(min_increment_value)+","+str(max_increment_value)+"\n")
	
	#Saving the calculation for next step
	new_inp.write("*RESTART, WRITE\n")
	
	#Displaced nodes characteristics 
	new_inp.write("*BOUNDARY\n")
	new_inp.write(Disp_node_set_name+","+str(first_degree_freedom)+","+str(last_degree_freedom)+","+str(disp_value)+"\n")

	#Fixed nodes
	new_inp.write("*BOUNDARY\n")
	new_inp.write(Fixed_node_set_name+",1,6,0\n")

	#Output files and values
	new_inp.write("*NODE PRINT, NSET="+Disp_node_set_name)
	if output_type=="Disp":
		new_inp.write("\nU\n")
	elif output_type=="Force":
		new_inp.write(",Totals=Only\nRF\n")
		
	new_inp.write("*END STEP")
	new_inp.close()
