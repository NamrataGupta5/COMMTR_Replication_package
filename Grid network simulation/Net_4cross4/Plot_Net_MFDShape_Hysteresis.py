# -*- coding: utf-8 -*-
"""
Created on Thu May 11 23:13:51 2023

@author: Namrata
"""
import numpy as np
import pandas as pd
import glob, os, shutil
import matplotlib.pyplot as plt
os.chdir(r'C:\Users\admin\OneDrive - IIT Bombay\COMMTR_3bin\Replication Package\Grid network simulation\Net_4cross4')


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


        
 
def MFD_df(fileloc, RunNo = 'AVG'):
    df = pd.read_csv(fileloc, sep =';')
    df = Data_Process(df)
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


#D1 : Lower Demand
D1_FT = MFD_df(r'.\Lower Demand\P0_0\LS.att')
D1_P0_G_Int = MFD_df(r'.\Lower Demand\P0_0.3\LS.att')
D1_P0_G1 = MFD_df(r'.\Lower Demand\P0_1\LS.att')
D1_P1_G_Int = MFD_df(r'.\Lower Demand\P1_0.3\LS.att')
D1_P1_G1 = MFD_df(r'.\Lower Demand\P1_1\LS.att')

#D2 : Higher Demand
D2_FT = MFD_df(r'.\Higher Demand\P0_0\LS.att')
D2_P0_G_Int = MFD_df(r'.\Higher Demand\P0_0.3\LS.att')
D2_P0_G1 = MFD_df(r'.\Higher Demand\P0_1\LS.att')
D2_P1_G_Int = MFD_df(r'.\Higher Demand\P1_0.3\LS.att')
D2_P1_G1 = MFD_df(r'.\Higher Demand\P1_1\LS.att')



dfArr = [D1_FT,D1_P0_G_Int, D1_P0_G1]
LegArr = ['$\gamma=0$','$\gamma=0.3$', '$\gamma=1$']
color =  ['r','b','k']
fig = plt.figure(figsize =(8,7))  
ax = plt.axes()    
for df, leg,c in zip(dfArr, LegArr,color):
    ax.plot(df['KL'],df['VL'], color=c, linestyle='-', linewidth= 2, label=leg)
ax.set_ylabel('$\overline{Q} \, (Veh/hr/lane)$')
ax.set_xlabel('$\overline{K} \, (Veh/km/lane)$')
ax.set_xlim(0, 106)
ax.set_xticks(np.arange(0, 106, 15))
ax.set_xticklabels(np.arange(0, 106, 15), fontsize=14)
ax.set_ylim(0, 750)
ax.set_yticks(np.arange(0, 705, 200))
ax.set_yticklabels(np.arange(0, 705, 200), fontsize=14)
ax.legend()
plt.savefig('P0_Hyst_Comp_l.pdf', format='pdf', bbox_inches='tight')
              
dfArr = [D1_FT,D1_P1_G_Int, D1_P1_G1]
LegArr = ['$\gamma=0$','$\gamma=0.3$', '$\gamma=1$']
color =  ['r','b','k']
fig = plt.figure(figsize =(8,7))  
ax = plt.axes()    
for df, leg,c in zip(dfArr, LegArr,color):
    ax.plot(df['KL'],df['VL'], color=c, linestyle='-', linewidth= 2, label=leg)
ax.set_ylabel('$\overline{Q} \, (Veh/hr/lane)$')
ax.set_xlabel('$\overline{K} \, (Veh/km/lane)$')
ax.set_xlim(0, 106)
ax.set_xticks(np.arange(0, 106, 15))
ax.set_xticklabels(np.arange(0, 106, 15), fontsize=14)
ax.set_ylim(0, 750)
ax.set_yticks(np.arange(0, 705, 200))
ax.set_yticklabels(np.arange(0, 705, 200), fontsize=14)
ax.legend()
plt.savefig('P1_Hyst_Comp_l.pdf', format='pdf', bbox_inches='tight')

dfArr = [D2_FT,D2_P0_G_Int, D2_P0_G1]
LegArr = ['$\gamma=0$','$\gamma=0.3$', '$\gamma=1$']
color =  ['r','b','k']
fig = plt.figure(figsize =(8,7))  
ax = plt.axes()    
for df, leg,c in zip(dfArr, LegArr,color):
    ax.plot(df['KL'],df['VL'], color=c, linestyle='-', linewidth= 2, label=leg)
ax.set_ylabel('$\overline{Q} \, (Veh/hr/lane)$')
ax.set_xlabel('$\overline{K} \, (Veh/km/lane)$')
ax.set_xlim(0, 106)
ax.set_xticks(np.arange(0, 106, 15))
ax.set_xticklabels(np.arange(0, 106, 15), fontsize=14)
ax.set_ylim(0, 750)
ax.set_yticks(np.arange(0, 705, 200))
ax.set_yticklabels(np.arange(0, 705, 200), fontsize=14)
ax.legend()
plt.savefig('P0_Hyst_Comp_H.pdf', format='pdf', bbox_inches='tight')
              
dfArr = [D2_FT,D2_P1_G_Int, D2_P1_G1]
LegArr = ['$\gamma=0$','$\gamma=0.3$', '$\gamma=1$']
color =  ['r','b','k']
fig = plt.figure(figsize =(8,7))  
ax = plt.axes()    
for df, leg,c in zip(dfArr, LegArr,color):
    ax.plot(df['KL'],df['VL'], color=c, linestyle='-', linewidth= 2, label=leg)
ax.set_ylabel('$\overline{Q} \, (Veh/hr/lane)$')
ax.set_xlabel('$\overline{K} \, (Veh/km/lane)$')
ax.set_xlim(0, 106)
ax.set_xticks(np.arange(0, 106, 15))
ax.set_xticklabels(np.arange(0, 106, 15), fontsize=14)
ax.set_ylim(0, 750)
ax.set_yticks(np.arange(0, 705, 200))
ax.set_yticklabels(np.arange(0, 705, 200), fontsize=14)
ax.legend()
plt.savefig('P1_Hyst_Comp_H.pdf', format='pdf', bbox_inches='tight')

