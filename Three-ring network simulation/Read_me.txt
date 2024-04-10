Input file name: 3rings.inpx
In Vissim model, change the loading rate (Veh/hr) in ring.
1) higher per-lane flow in ring 3 (4d1=4d2=d3) -> (20,10,40)
2) Equal per-lane flow in rings (d1=d2=d3) -> (30,15,15)
3) higher per-lane flow in ring 1 (d1=4d3=4d3) -> (48,6,6)

Python Scripts 
1) '3Ring_MFD_DiffControlPolicies.py' - to execute studied control logics in Vissim
2) 'Plot_3Ring_MFDShape_LoadingRate.py' - to plot simulation results

Comman settings in each scenario
- Phases:
	Phase 1: Ring 1-> Ring 2
	Phase 2: Ring 1-> Ring 3
	Phase 3: Ring 2-> Ring 1
	Phase 4: Ring 3-> Ring 1
- Cycle time = 60Sec
- Ring length: 1000 m
- All vehicles are car with desired speed: 60 km/hr
- Number of repetition: 40

- Link segment results file of each experiment is saved and processed to save aggregate parameters (density, speed, volume) of each ring. Also, we store flow on the connector links between rings.
- The data files (processed link segment results) are named accordingly and saved in appropriate folders