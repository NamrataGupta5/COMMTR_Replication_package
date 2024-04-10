Input file name: Net_2cross2.inpx
In Vissim model, change the loading rate (Veh/hr) on each incoming link of an intersection.
1) higher per-lane flow in vertical links (4d1=4d2=d3) -> (20,10,40)
2) Equal per-lane flow in all links (d1=d2=d3) -> (30,15,15)
3) higher per-lane flow in horizontal links (d1=4d3=4d3) -> (48,6,6)

Python Scripts 
1) 'Net_2cross2_MFD_DiffControlPolicies.py' - to execute studied control logics in Vissim
2) 'Plot_Net_MFDShape_LoadingRate.py' - to plot simulation results

- Link segment results file of each experiment is saved and processed to save aggregate parameters (density, speed, volume) of each ring. Also, we store flow on the connector links between rings.
- The exported link segment result files are named 'LS.att' and saved at appropriate folder