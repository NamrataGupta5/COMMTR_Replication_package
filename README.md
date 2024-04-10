# COMMTR_Replication_package
This document gives summary of all the folders. Each folder in this directory contains
- a separate 'read_me' file to explain the experiment settings
- necessary python scripts, vissim files, data files, and obtained figures
- Python scripts includes sufficient remarks and are self-explanatory

The following gives brief description about the folders.
1) 'Flow within bin and outflow from a bin' 
	--> To obtain expression discussed in Section 4.2-4.3
	--> Ring microsimulation results to obtain Fig. 4-5
2) 'Stability analyses using three-bin'
	--> to obtain phase diagrams and MFDs for discussed TSCs (Eq. 27-30)
	--> Utilizes the bin dynamics (Eq. 1 & 10), equilibria cond (Eq. 11), and stability condition (Eq. 21 & 26) 
	--> To obtain Fig. 6-8 in Section 5.2
3) 'Three-ring network simulation'
	--> To verify theoretical predictions from three-bin analyses
	--> Microsimulation results of three-ring network
	--> To obtain Fig. 10-12 in Section 6.3-6.5
4) 'Grid network simulation'
	--> To validate prediction in presence of neighboring intersections and nonperiodic boundary conditions
	--> Microsimulation results of 2*2 and 4*4 grid networks
	--> To obtain Fig. 14 & 16 in Section 7

Versions of software and libraries
Versions of software and python libraries
1) Python 3.8 
2) pandas 1.3.3
3) numpy 1.21.5
4) matplotlib 3.4.3
5) PySimpleGUI 4.45.0
6) Pywin32 302
7) os
8) re
9) warnings
10) datetime
11) PTV Vissim 6.0
