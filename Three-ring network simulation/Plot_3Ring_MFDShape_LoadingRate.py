# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 10:51:37 2022

@author: admin
"""

import os
os.chdir(r'C:\Users\admin\OneDrive - IIT Bombay\COMMTR_3bin\Replication Package\Three-ring network simulation')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


nice_fonts = {
        # "text.usetex": True,
        "font.family": 'Times New Roman',
        "axes.labelsize": 20,
        "font.size": 14,
        "legend.fontsize": 14,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
}

plt.rcParams.update(nice_fonts)

#D1 : Demand_(20,10,40)

Fnames = ['Demand_(20,10,40)\P0_0\P0_G_0_Avg.att',
          'Demand_(20,10,40)\P0_0.3\P0_G_0.3_Avg.att',
          'Demand_(20,10,40)\P0_1\P0_G_1_Avg.att',
          'Demand_(20,10,40)\P1_0.3\P1_G_0.3_Avg.att',
          'Demand_(20,10,40)\P1_1\P1_G_1_Avg.att']
Val = []
for FN in Fnames:
    df =  pd.read_csv(FN, sep =';')
    df = df[df['AvgQ']>0]
    Val.append(df[['AvgK','AvgQ']].values)
D1_FT, D1_P0_G_Int, D1_P0_G1, D1_P1_G_Int, D1_P1_G1 = Val


#D2 : Demand_(30,15,15)
Fnames = ['Demand_(30,15,15)\P0_0\P0_G_0_Avg.att',
          'Demand_(30,15,15)\P0_0.3\P0_G_0.3_Avg.att',
          'Demand_(30,15,15)\P0_1\P0_G_1_Avg.att',
          'Demand_(30,15,15)\P1_0.3\P1_G_0.3_Avg.att',
          'Demand_(30,15,15)\P1_1\P1_G_1_Avg.att']
Val = []
for FN in Fnames:
    df =  pd.read_csv(FN, sep =';')
    df = df[df['AvgQ']>0]
    Val.append(df[['AvgK','AvgQ']].values)
D2_FT, D2_P0_G_Int, D2_P0_G1, D2_P1_G_Int, D2_P1_G1 = Val

#D3 : Demand_(48,6,6)
Fnames = ['Demand_(48,6,6)\P0_0\P0_G_0_Avg.att',
          'Demand_(48,6,6)\P0_0.3\P0_G_0.3_Avg.att',
          'Demand_(48,6,6)\P0_1\P0_G_1_Avg.att',
          'Demand_(48,6,6)\P1_0.3\P1_G_0.3_Avg.att',
          'Demand_(48,6,6)\P1_1\P1_G_1_Avg.att',
          ]
Val = []
for FN in Fnames:
    df =  pd.read_csv(FN, sep =';')
    df = df[df['AvgQ']>0]
    Val.append(df[['AvgK','AvgQ']].values)
D3_FT, D3_P0_G_Int, D3_P0_G1, D3_P1_G_Int, D3_P1_G1 = Val


for val,leg in zip([[D1_FT,D2_FT,D3_FT],
                    [D1_P0_G_Int,D2_P0_G_Int,D3_P0_G_Int],
                    [D1_P0_G1,D2_P0_G1,D3_P0_G1],
                    [D1_P1_G_Int,D2_P1_G_Int,D3_P1_G_Int],
                    [D1_P1_G1,D2_P1_G1,D3_P1_G1]],
                   ['FT','P0_G0.3', 'P0_G1','P1_G0.3', 'P1_G1']):
    #Comparing all gamma for differernt loading rates
    fig, ax = plt.subplots(1, 1,figsize =(8,7))
    ax.plot(val[0][:,0],val[0][:,1],color='r', linestyle='-', linewidth= 2, label=r'$\left(4d_1 = 4d_2 = d_3 \right)$')
    ax.plot(val[1][:,0],val[1][:,1],color='b', linestyle='-', linewidth= 2, label=r'$\left(d_1 = d_2 = d_3\right)$')
    ax.plot(val[2][:,0],val[2][:,1],color='k', linestyle='-', linewidth= 2, label=r'$\left(d_1 = 4d_2 = 4d_3\right)$')
    ax.set_ylabel('$\overline{Q} \, (Veh/hr/lane)$')
    ax.set_xlabel('$\overline{K} \, (Veh/km/lane)$')
    ax.set_xlim(0, 155)
    ax.set_xticks(np.arange(0, 151, 15))
    ax.set_xticklabels(np.arange(0, 151, 15), fontsize=14)
    ax.set_ylim(0, 750)
    ax.set_yticks(np.arange(0, 705, 200))
    ax.set_yticklabels(np.arange(0, 705, 200), fontsize=14)
    ax.legend()
    plt.savefig(leg+'.pdf', format='pdf', bbox_inches='tight')

