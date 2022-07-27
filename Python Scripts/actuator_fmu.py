import numpy as np
from scipy.optimize import fsolve
step=0

#Actuators characteristics
x1=0
y1=50
x2=50
y2=0
l1=50
l2=50

#Inputs
delta_l1=10
delta_l2=20

#Outputs
xc=0
yc=0
ux=0
uy=0

def init_equations(tuple):
    xc,yc=tuple
    return [(xc-x1)**2+(yc-y1)**2-l1**2,(xc-x2)**2+(yc-y2)**2-l2**2]

def step_equations(tuple):
    ux,uy=tuple
    return [(xc+ux-x1)**2+(yc+uy-y1)**2-(l1+delta_l1)**2,(xc+ux-x2)**2+(yc+uy-y2)**2-(l2+delta_l2)**2]

def actuators(x1,x2,y1,y2,l1,l2,delta_l1,delta_l2):
    global xc
    global yc
    global ux
    global uy
    if step==0:
        xc, yc=  fsolve(init_equations, (x2,y1))
        print(f"xc={xc}\nyc={yc}\nux={ux}\nuy={uy}")
    else :
        ux, uy= fsolve(step_equations, (delta_l1,delta_l2))
        print(f"ux={ux}\nuy={uy}\nxc={xc}\nyc={yc}")

#
# def inv_jacobian(matrix):
#     inv_jac=np.empty_like(matrix)
#     coef=1/(2*(2*x1*x2+(x1-x2)*(xc-yc+ux-uy)))
#     inv_jac_calc=coef*numpy.linalg.inv(matrix)
#     inv_jac[0,0]=matrix[1,1]
#     inv_jac[0,1]=-matrix[0,1]
#     inv_jac[1,0]=-matrix[1,0]
#     inv_jac[1,1]=-matrix[0,0]
#
#     return None
#
# def jacobian():
#     jac=np.empty((2,2))
#     jac[0,0]=2*(xc+ux-x1)
#     jac[0,1]=2*(yc+uy-x1)
#     jac[1,0]=2*(xc+ux-x2)
#     jac[1,1]=2*(yc+uy-x2)
#     return jac
