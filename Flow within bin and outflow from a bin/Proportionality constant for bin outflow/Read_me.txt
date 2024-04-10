Input file name: 3rings.inpx
In Vissim model, change the following setting.
1) FT_SameTR: Turn ratios (0.2,0.2,0.2,0.2) and green time (15,15,15,15) -> Siganlized intersection with same Turn ratio
2) FT_DiffTR: Turn ratios (0.1,0.1,0.2,0.2) and green time (15,15,15,15) -> Siganlized intersection with different Turn ratio
1) Unsig_SameTR: Turn ratios (0.2,0.2,0.2,0.2) and green time (60,60,60,60) -> Unsiganlized intersection with same Turn ratio
2) UnSig_DiffTR: Turn ratios (0.1,0.1,0.2,0.2) and green time (60,60,60,60) -> unsiganlized intersection with different Turn ratio
Comman settings in each scenario
- Phases:
	Phase 1: Ring 1-> Ring 2
	Phase 2: Ring 1-> Ring 3
	Phase 3: Ring 2-> Ring 1
	Phase 4: Ring 3-> Ring 1
- Cycle time = 60Sec
- Ring length: 1000 m
- All vehicles are car with desired speed: 60 km/hr
- Number of repetition: 10

- Link segment results file of each experiment is saved and processed to save aggregate parameters (density, speed, volume) of each ring. Also, we store flow on the connector links between rings.
- The data files (processed link segment results) are named accordingly