import re
test =r"C:\Users\marcu\OneDrive\Desktop\test\run_test\Step_8\init_Step_8.dat"
def update_disp(filename):
    file=open(filename,'r')
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
    return result_disp

#result_disp.append(lines.split("  "))
#
# s = "12 hello 52 19 some random 15 number"
# # Extract numbers and cast them to int
# list_of_nums = map(int, re.findall('\d+', s))
# print list_of_nums
#
#
# files = open(fo, 'r')
# for i, line in enumerate(files):
# if i%8 == 2:
# print line
# elif i%8 == 5:
# print line
#
#
#
# for char in (line [:10].strip()):
# if s.isdi
# print(lines [:10].strip())#I'm going to suppose that the number of nodes is less than 1E9 since there are only 10 collums for the node numbers