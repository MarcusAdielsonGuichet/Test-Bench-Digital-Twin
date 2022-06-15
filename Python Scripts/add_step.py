def add_step(inp_file):
	previous_inp=open(inp_file, 'r')
	new_inp=open("new_inp_file.inp", 'w')
	for line in previous_inp:
		if "*END STEP" in line:
			end_step_count+=1
			if end_step_count==nb-1:
				new_inp.write("*STEP, NLGEOM, INC=1000000\n")
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

#experimental
def step_with_restart():#need a previous run, and something with the .rin and .rout for the previous run file
	new_inp=open("new_inp_file.inp", 'w')
	new_inp.write("*RESTART, READ\n")
	
	new_inp.write("*STEP, NLGEOM, INC=1000000\n")
	new_inp.write("*DYNAMIC\n")
	new_inp.write(str(first_increment_value)+","+str(step_duration)+","+str(min_increment_value)+","+str(max_increment_value)+"\n")
	
	new_inp.write("*RESTART, WRITE\n")
	
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
	
	
	
