# Understanding the CalculiX FEA Process

In this folder is an example of a static step analysis implemented into CaluliX

# The input file or filename.inp
This file is the one of the two most important part of the CalculiX solver process, as it defines the entire analysis you'll be working, aka your virtual test bench.
It is decomposed in several parts:
- The node coordinates of your model
- The type of mesh elements you've chosen(tetrahedron, hexahedron...)
- The dimension of the mesh elements(3D, 2D or 1D)
- The type of FEM element type (solid, shell, beam, fluid...)
- The node sets receving constraints
- The material of the model
- The type of section, if necessary
- The step(s)

Let's break this all down!

# The node coordinates of your model

This defines the global cartesian coordinates of every single point of your mesh.
In FreeCAD, this process is automated by the ... function, in the ... module.

# The type of mesh elements you've chosen(tetrahedron, hexahedron...), dimension of the mesh elements(3D, 2D or 1D) and type of FEM element type (solid, shell, beam, fluid...)

This part requires some understanding of your model and the simplifications you can apply to it. By default, stick to 3D Solid Tetrahedron, or TYPE=C3D10 in the CCX inp file, as it the baseline for any element in the real world.  

Shell elements are useful when dealing with...
Beam elements, on the other hand,...

If you want further information, fell free to dive deeper into the CGX and CCX manual, page 130 in CGX and page 88 in CCX for element types, page 386 for inp definition in CCX.

# The node sets receving constraints

This group nodes that correspond to the constraints defined by the user.
In FreeCAD, this process is automated by the ... function, in the ... module.
In PrePromax, this process is automated by ?

# The material of the model

This defines the working material defined by the user for the model.

# The type of section, if necessary
Not sure about this one yet...

# The step(s)
This part is the most crucial part, because it defines the whole analysis conducted on the model

It always start with the "*STEP, Nlgeom, Inc=Max_increments_value\n" keycard

The Nlgeom keyword allows for great displacement inside of the analysis, which seems to be the case with our test bench.
The Inc keyword defines the max number of increments to be calculated in the step. Be warry that this number must account for at least the number of time increments necessary for the whole duration of the step(max 100 0.1s increments for a 1s step is good, but 5 is not), or the solver will not proceed to the next step, in multistep analysis

And is followed by the type of Analysis conducted
"*Static", "*Dynamic", "*Frequency", "*Modal Dynamic" and so on...list of analysis types and implications specified in section 6.9 of the CCX manual

Then the time characteristics of the step which are as follow:
“First_time_increment_value, Step_duration_value, Min_increment_value, Max_increment_value”
- First increment of the step means first values will be calculated after First_time_increment_value seconds have passed
- Duration of the step means the analysis defined for this step is Step_duration_value seconds long
- Minimal increment value means that the next increment calculation in the step needs to be at least Min_increment_value seconds after the previous one
- Max increment value means the next increment calculation in the step needs to be at best done Max_increment_value seconds after the previous one

Then we have our inputs(loads, contraints...)
Constraints are identified with the "*Boundary" keycard (and can be repeated for as many constraints that need to be defined) and are followed by(section 7.4 CCX Manual):
- The node/node sets
- The first degree of freedom affected
- The last degree of freedom affected
- The value of the constraint
Here's an example:

*Boundary
ConstraintDisplacement, 1, 1, -24
*Boundary
Internal_Selection-1_Fixed-1, 1, 6, 0

The first two lines defines a displacement of -24mm on the x translation for the node set defined as ConstraintDisplacement
The next two lines defines a fixed constraint on all degrees of freedom(x,y,z translation and rotation) for the nodes in the Internal_Selection-1_Fixed-1 node set.

Loads on the other hand are definded by the "*Cload, Op=New/Mod" or "*Dload, Op=New/Mod" keywords with the following indicators (section 7.15 and 7.39 CCX Manual):
- The node/node sets
- The degree of freedom affected
- The value of the load

Then we have our outputs files(frd and dat), defined with "*NODE FILE", "*EL FILE", "*NODE PRINT, NSET=set_name" and other parameters depending how what one wants from the analysis.(section 6.13 of CCX manual and all output variables)
"*NODE FILE"(frd output) and "*NODE PRINT"(dat output), give out info about node(displacements for example
"*EL FILE" gives out info about averages from nodes(stresses for example

And finally the step is concluded with the "*End step" card

Step blocks can be repeated in chain for however many steps required

For the second part, I'm trying to understand how to save each step in the memory, if it possible, so we can run Calculix dynamicaly for the step by step analysis.

For the post processing part, I recommend using PreProMax, as it can animate each increment of each step into a movie so you can witness firstand the result.
