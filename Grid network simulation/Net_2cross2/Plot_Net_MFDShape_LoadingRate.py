# -*- coding: utf-8 -*-
"""
Created on Thu May 11 23:13:51 2023

@author: Namrata
"""
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
os.chdir(r'C:\Users\admin\OneDrive - IIT Bombay\COMMTR_3bin\Replication Package\Grid network simulation\Small Network')

def Data_Process(df, per_link=1):
    x = df['Seg'].values
    y = np.array([int(a.split('-')[0]) for a in x])
    df['Link'] = y
    x= df['Time'].values
    y = np.array([int(a.split('-')[0]) for a in x])
    df['StTime'] = y
    # l = np.arange(1,61,1)
    # df = df[df['Link'].isin(l)]
    df =df[['SR','StTime', 'Density', 'Volume', 'Length', 'Lanes', 'Link']]
    if per_link==1:
        df['Volume'] = df['Volume'].div(df['Lanes'], axis = 'index').values
        df['Density'] = df['Density'].div(df['Lanes'], axis = 'index').values
    df['TL'] = df['Lanes'].mul(df['Length'], axis = 'index').values
    df['KL'] = df['Density'].mul(df['TL'], axis = 'index').values
    df['VL'] = df['Volume'].mul(df['TL'], axis = 'index').values
    return df

        
 
def MFD_df(fileloc, RunNo = 'AVG',LessLinks = True):
    df = pd.read_csv(fileloc, sep =';')
    df = Data_Process(df)
    if LessLinks==True:
        l = np.array([5,6,34,
                  9,10,14,
                  15,16,20,
                  1,2,35,
                  21,22,26,
                  27,28,32])
        # l = np.arange(1,61,1)
        df = df[df['Link'].isin(l)]
    df1 = df[df['SR']==RunNo]
    TotLen = df1[df1['StTime']==0]['TL'].sum()
    g = df1.groupby('StTime')
    df_mean = g.sum()[['KL','VL']]/TotLen
    return df_mean  
          
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
D1_FT = MFD_df(r'.\Demand_(20,10,40)\P0_0\LS.att')
D1_P0_G_Int = MFD_df(r'.\Demand_(20,10,40)\P0_0.3\LS.att')
D1_P0_G1 = MFD_df(r'.\Demand_(20,10,40)\P0_1\LS.att')
D1_P1_G_Int = MFD_df(r'.\Demand_(20,10,40)\P1_0.3\LS.att')
D1_P1_G1 = MFD_df(r'.\Demand_(20,10,40)\P1_1\LS.att')

#D2 : Demand_(30,15,15)
D2_FT = MFD_df(r'.\Demand_(30,15,15)\P0_0\LS.att')
D2_P0_G_Int = MFD_df(r'.\Demand_(30,15,15)\P0_0.3\LS.att')
D2_P0_G1 = MFD_df(r'.\Demand_(30,15,15)\P0_1\LS.att')
D2_P1_G_Int = MFD_df(r'.\Demand_(30,15,15)\P1_0.3\LS.att')
D2_P1_G1 = MFD_df(r'.\Demand_(30,15,15)\P1_1\LS.att')

#D3 : Demand_(48,6,6)
D3_FT = MFD_df(r'.\Demand_(48,6,6)\P0_0\LS.att')
D3_P0_G_Int = MFD_df(r'.\Demand_(48,6,6)\P0_0.3\LS.att')
D3_P0_G1 = MFD_df(r'.\Demand_(48,6,6)\P0_1\LS.att')
D3_P1_G_Int = MFD_df(r'.\Demand_(48,6,6)\P1_0.3\LS.att')
D3_P1_G1 = MFD_df(r'.\Demand_(48,6,6)\P1_1\LS.att')

for val,leg in zip([[D1_FT,D2_FT,D3_FT],
                    [D1_P0_G_Int,D2_P0_G_Int,D3_P0_G_Int],
                    [D1_P0_G1,D2_P0_G1,D3_P0_G1],
                    [D1_P1_G_Int,D2_P1_G_Int,D3_P1_G_Int],
                    [D1_P1_G1,D2_P1_G1,D3_P1_G1]],
                   ['FT','P0_G0.3', 'P0_G1','P1_G0.3', 'P1_G1']):
    #Comparing all gamma for differernt loading rates
    fig, ax = plt.subplots(1, 1,figsize =(8,7))
    ax.plot(val[0]['KL'].values,val[0]['VL'].values,color='r', linestyle='-', linewidth= 2, label=r'$\left(4d_1 = 4d_2 = d_3 \right)$')
    ax.plot(val[1]['KL'],val[1]['VL'],color='b', linestyle='-', linewidth= 2, label=r'$\left(d_1 = d_2 = d_3\right)$')
    ax.plot(val[2]['KL'],val[2]['VL'],color='k', linestyle='-', linewidth= 2, label=r'$\left(d_1 = 4d_2 = 4d_3\right)$')
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