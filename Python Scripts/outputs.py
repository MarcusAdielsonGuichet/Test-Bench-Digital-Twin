import re
import numpy as np
test =r"C:\Users\marcu\OneDrive\Desktop\test\run_test\Step_1\init_Step_1.sti"
def get_disp(dat_filename):
    file=open(dat_filename,'r')
    result_disp=[]
    for i, line in enumerate(file):
        if i>=3:
            node_disp_values=[]
            #Node number
            node_disp_values.append(int(line[:10].strip()))
            #Ux
            node_disp_values.append(float(line[12:24].strip()))
            #Uy
            node_disp_values.append(float(line[26:39].strip()))
            #Uz
            node_disp_values.append(float(line[40:].strip()))
            result_disp.append(node_disp_values)
    file.close()#is this necessary?
    return result_disp

def get_forces(dat_filename):
    file=open(dat_filename,'r')
    for i, line in enumerate(file):
        if i>=3:
            result_forces_values=[]
            #Fx
            result_forces_values.append(float(line[3:21].strip()))
            #Fy
            result_forces_values.append(float(line[22:34].strip()))
            #Fz
            result_forces_values.append(float(line[35:].strip()))
            break
    file.close()#is this necessary?
    return result_forces_values

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

#
#
#
#
#
#
#
#
# #result_disp.append(lines.split("  "))
# #
# # s = "12 hello 52 19 some random 15 number"
# # # Extract numbers and cast them to int
# # list_of_nums = map(int, re.findall('\d+', s))
# # print list_of_nums
# #
# #
# # files = open(fo, 'r')
# # for i, line in enumerate(files):
# # if i%8 == 2:
# # print line
# # elif i%8 == 5:
# # print line
# #
# #
# #
# # for char in (line [:10].strip()):
# # if s.isdi
# # print(lines [:10].strip())#I'm going to suppose that the number of nodes is less than 1E9 since there are only 10 collums for the node numbers