# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 19:07:46 2022
- To analyse MFD shape variation with signal plan
- To understand expression of flow within bins
- Please make sure to change directory

@author: Namrata
"""

import os
os.chdir(r'C:\Users\admin\OneDrive - IIT Bombay\COMMTR_3bin\Replication Package\Flow within bin and outflow from a bin\MFD_for fixed time_diff signal plan')

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
def binflow(k, g_avg, s=60, kjam = 150, kc =40):
    w = s*kc/(kjam-kc)
    return min([s*k, s*kc*g_avg, w*(kjam-k)])

x = np.arange(0,150,10)

#RingFD - From 3 Ring model with unsignalized intersection
df_RingFD = pd.read_csv(r'.\GrTm_60_60_60_60.att', sep =';')
R1 = df_RingFD[['K1','V1']].values
R2 = df_RingFD[['K2','V2']].values
R3 = df_RingFD[['K3','V3']].values
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(R1[:,0],R1[:,1],color='r', linestyle='-', linewidth= 2, label='Ring 1 $(n=2)$')
ax.plot(R2[:,0],R2[:,1],color='b', linestyle='-', linewidth= 2, label='Ring 2 $(n=1)$')
ax.plot(R3[:,0],R3[:,1],color='g', linestyle='-', linewidth= 2, label='Ring 3 $(n=1)$')
ax.plot(x,np.array([binflow(k, 1) for k in x]),color='k', linestyle='--', linewidth= 3, label='Expected')
ax.set_ylabel('$q_{b,t} \, (Veh/hr/lane)$')
ax.set_xlabel('$k_{b,t} \, (Veh/km/lane)$')
ax.set_xlim(0, 160)
ax.set_xticks(np.arange(0, 161, 20))
ax.set_xticklabels(np.arange(0, 161, 20), fontsize=14)
ax.set_ylim(0, 2550)
ax.set_yticks(np.arange(0, 2550, 500))
ax.set_yticklabels(np.arange(0, 2550, 500), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'RingFD.pdf', format='pdf', bbox_inches='tight')

#Reading data files for sigalized intersection
df_0_40_10_10 = pd.read_csv(r'.\GrTm_0_40_10_10.att', sep =';')


df_10_20_15_15 = pd.read_csv(r'.\GrTm_10_20_15_15.att', sep =';')
df_15_15_15_15 = pd.read_csv(r'.\GrTm_15_15_15_15.att', sep =';')
df_0_30_15_15 = pd.read_csv(r'.\GrTm_0_30_15_15.att', sep =';')

df_5_15_20_20 = pd.read_csv(r'.\GrTm_5_15_20_20.att', sep =';')
df_10_10_20_20 = pd.read_csv(r'.\GrTm_10_10_20_20.att', sep =';')
df_0_20_20_20 = pd.read_csv(r'.\GrTm_0_20_20_20.att', sep =';')
df_20_0_20_20 = pd.read_csv(r'.\GrTm_20_0_20_20.att', sep =';')
df_20_20_10_10 = pd.read_csv(r'.\GrTm_20_20_10_10.att', sep =';')
df_10_30_10_10 = pd.read_csv(r'.\GrTm_10_30_10_10.att', sep =';')

# Rings with average green time g=1/3 (or average green time of a ring = 20 sec)
L1_20 = df_0_20_20_20[['K2','V2']].values
L2_0_40 = df_0_40_10_10[['K1','V1']].values
L2_20_20 = df_20_20_10_10[['K1','V1']].values
L2_10_30 = df_10_30_10_10[['K1','V1']].values
#g=1/3 fig
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(L1_20[:,0],L1_20[:,1],color='r', linestyle='-', linewidth= 2, label='$n=1, g = \dfrac{1}{3}$')
ax.plot(L2_10_30[:,0],L2_10_30[:,1],color='b', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{6},\dfrac{1}{2}\right)$')
ax.plot(L2_20_20[:,0],L2_20_20[:,1],color='g', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{3},\dfrac{1}{3}\right)$')
ax.plot(L2_0_40[:,0],L2_0_40[:,1],color='k', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{2}{3},0\right)$')
ax.plot(x,np.array([binflow(k, 1/3) for k in x]),color='k', linestyle='--', linewidth= 3, label='Expected')
ax.set_ylabel('$q_{b,t} \, (Veh/hr/lane)$')
ax.set_xlabel('$k_{b,t} \, (Veh/km/lane)$')
ax.set_xlim(0, 200)
ax.set_xticks(np.arange(0, 161, 20))
ax.set_xticklabels(np.arange(0, 161, 20), fontsize=14)
ax.set_ylim(0, 1150)
ax.set_yticks(np.arange(0, 1150, 200))
ax.set_yticklabels(np.arange(0, 1150, 200), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'BinFlow_GrTm1.pdf', format='pdf', bbox_inches='tight')

# Rings with average green time g=1/4 (or average green time of a ring = 15 sec)
L1_15 = df_15_15_15_15[['K2','V2']].values
L2_15_15 = df_15_15_15_15[['K1','V1']].values
L2_10_20 = df_10_20_15_15[['K1','V1']].values
L2_0_30 =  df_0_30_15_15[['K1','V1']].values
#g=1/4 fig
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(L1_15[:,0],L1_15[:,1],color='r', linestyle='-', linewidth= 2, label='$n=1, g = \dfrac{1}{4}$')
ax.plot(L2_10_20[:,0],L2_10_20[:,1],color='b', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{6},\dfrac{1}{3}\right)$')
ax.plot(L2_15_15[:,0],L2_15_15[:,1],color='g', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{4},\dfrac{1}{4}\right)$')
ax.plot(L2_0_30[:,0],L2_0_30[:,1],color='k', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{2},0\right)$')
ax.plot(x,np.array([binflow(k, 1/4) for k in x]),color='k', linestyle='--', linewidth= 3, label='Expected')
ax.set_ylabel('$q_{b,t} \, (Veh/hr/lane)$')
ax.set_xlabel('$k_{b,t} \, (Veh/km/lane)$')
ax.set_xlim(0, 200)
ax.set_xticks(np.arange(0, 161, 20))
ax.set_xticklabels(np.arange(0, 161, 20), fontsize=14)
ax.set_ylim(0, 1150)
ax.set_yticks(np.arange(0, 1150, 200))
ax.set_yticklabels(np.arange(0, 1150, 200), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'BinFlow_GrTm2.pdf', format='pdf', bbox_inches='tight')


## Rings with average green time g=1/6 (or average green time of a ring = 10 sec)
L1_10 = df_0_40_10_10[['K2','V2']].values
L2_5_15 = df_5_15_20_20[['K1','V1']].values
L2_10_10 = df_10_10_20_20[['K1','V1']].values
L2_0_20 = df_0_20_20_20[['K1','V1']].values
L2_20_0 = df_20_0_20_20[['K1','V1']].values
L2_10_30 = df_10_30_10_10[['K1','V1']].values
#g=1/6 fig
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(L1_10[:,0],L1_10[:,1],color='r', linestyle='-', linewidth= 2, label='$n=1, g = \dfrac{1}{6}$')
ax.plot(L2_5_15[:,0],L2_5_15[:,1],color='b', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{12},\dfrac{1}{4}\right)$')
ax.plot(L2_10_10[:,0],L2_10_10[:,1],color='g', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{6},\dfrac{1}{6}\right)$')
ax.plot(L2_0_20[:,0],L2_0_20[:,1],color='k', linestyle='-', linewidth= 2, label=r'$n=2, g = \left(\dfrac{1}{3},0\right)$')
ax.plot(x,np.array([binflow(k, 1/6) for k in x]),color='k', linestyle='--', linewidth= 3, label='Expected')
ax.set_ylabel('$q_{b,t} \, (Veh/hr/lane)$')
ax.set_xlabel('$k_{b,t} \, (Veh/km/lane)$')
ax.set_xlim(0, 200)
ax.set_xticks(np.arange(0, 161, 20))
ax.set_xticklabels(np.arange(0, 161, 20), fontsize=14)
ax.set_ylim(0, 1150)
ax.set_yticks(np.arange(0, 1150, 200))
ax.set_yticklabels(np.arange(0, 1150, 200), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'BinFlow_GrTm3.pdf', format='pdf', bbox_inches='tight')




