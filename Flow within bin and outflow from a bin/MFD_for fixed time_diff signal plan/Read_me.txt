Input file name: 3rings.inpx
In Vissim model, change the signal plans as follows. Total cycle time = 60 sec.
1) (0,20,20,20)
2) (0,30,15,15)
3) (0,40,10,10)
4) (5,15,20,20)
5) (10,10,20,20)
6) (10,20,15,15)
7) (10,30,10,10)
8) (15,15,15,15)
9) (20,0,20,20)
10) (20,20,10,10)
11) (60,60,60,60) -> Unsignalized intersection
Comman settings in each scenario
- Phases:
	Phase 1: Ring 1-> Ring 2
	Phase 2: Ring 1-> Ring 3
	Phase 3: Ring 2-> Ring 1
	Phase 4: Ring 3-> Ring 1
- No interaction between rings, i.e., turn ratio = 0
- Ring length: 1000 m
- All vehicles are car with desired speed: 60 km/hr
- Number of repetition: 10

- Link segment results file of each experiment is saved and processed to save aggregate parameters (density, speed, volume) of each ring.
- The data files (processed link segment results) are named accordingly

Naming of figure file
- GrTm1 -> Average green time alloted to a ring = 20sec
- GrTm2 -> Average green time alloted to a ring = 15sec
- GrTm3 -> Average green time alloted to a ring = 10sec
- RingFD -> MFD for unsignalized rings