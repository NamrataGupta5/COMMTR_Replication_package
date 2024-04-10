Input file name: Net_2cross2.inpx
In Vissim model, change the loading rate (Veh/hr) on each incoming link of an intersection.
1) Lower demand -> Peak period demand 200 veh/hr/lane
2) Higher demand -> Peak period demand 300 veh/hr/lane

Python Scripts 
1) 'Net_4cross4_MFD_Hysteresis.py' - to execute studied control logics in Vissim
2) 'Plot_Net_MFDShape_Hysteresis.py' - to plot simulation results

- Link segment results file of each experiment is saved and processed to save aggregate parameters (density, speed, volume) of each ring. Also, we store flow on the connector links between rings.
- The exported link segment result files are named 'LS.att' and saved at appropriate folder