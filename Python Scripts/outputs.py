import re
import numpy as np
test =r"C:\Users\marcu\OneDrive\Desktop\test\force_disp_dat\force_disp_dat.dat"

def get_disp(dat_filename):
    file=open(dat_filename,'r')
    result_disp=[]
    disp_section=False
    for line in file:
        if len(line.split())>1:
            if line.split()[0]=="displacements":
                disp_section=True
            if line.split()[0].isnumeric()==False and line.split()[0]!="displacements":
                disp_section=False
            if disp_section==True and line.split()[0].isnumeric():#Verfication for non-blank lines and disp section
                node_nb,ux,uy,uz=int(line.split()[0]),float(line.split()[1]),float(line.split()[2]),float(line.split()[3])
                result_disp.append([node_nb,ux,uy,uz])
    file.close()#is this necessary?
    return result_disp

def get_node_forces(dat_filename):
    file=open(dat_filename,'r')
    result_forces=[]
    node_force_section=False
    for line in file:
        if len(line.split())>1:
            if line.split()[0]=="forces":
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

def get_force_sum(dat_filename):
    file=open(dat_filename,'r')
    forces_section=False
    result_force_sum=[]
    for line in file:
        if len(line.split())>1:
            if "total force"in line:
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