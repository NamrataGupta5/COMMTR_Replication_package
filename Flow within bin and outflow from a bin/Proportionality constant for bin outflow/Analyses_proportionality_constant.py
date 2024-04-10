# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 19:07:46 2022

- To understand expression of outflow from bins
- Please make sure to change directory

@author: Namrata
"""

import os
os.chdir(r'C:\Users\admin\OneDrive - IIT Bombay\COMMTR_3bin\Replication Package\Flow within bin and outflow from a bin\Proportionality constant for bin outflow')

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

# Signalized + Same turn ratio
df_FT_SameTR = pd.read_csv(r'.\FT_SameTR.att', sep =';')
FT_SameTR_Factor = df_FT_SameTR[['x12', 'x13', 'x21','x31']].values
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(FT_SameTR_Factor[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.2,$ $n_{1}=2$')
ax.plot(FT_SameTR_Factor[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.2,$ $n_{1}=2$')
ax.plot(FT_SameTR_Factor[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(FT_SameTR_Factor[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$C_{b,m} = F_{b,m}(\vec{K}_t)/q_{b,t}$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 301)
ax.set_xticks(np.arange(0, 301,50))
ax.set_xticklabels(np.arange(0, 301, 50), fontsize=14)
ax.set_ylim(0, 0.8)
ax.set_yticks(np.round(np.arange(0, 0.85, 0.2),1))
ax.set_yticklabels(np.round(np.arange(0, 0.85, 0.2),1), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'FT_SameTR_Factor.pdf', format='pdf', bbox_inches='tight')

# Signalized + Diff turn ratio
df_FT_DiffTR = pd.read_csv(r'.\FT_DiffTR.att', sep =';')
FT_Diff_Factor = df_FT_DiffTR[['x12', 'x13', 'x21','x31']].values

fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(FT_Diff_Factor[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.1,$ $n_{1}=2$')
ax.plot(FT_Diff_Factor[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.1,$ $n_{1}=2$')
ax.plot(FT_Diff_Factor[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(FT_Diff_Factor[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$C_{b,m} = F_{b,m}(\vec{K}_t)/q_{b,t}$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 301)
ax.set_xticks(np.arange(0, 301,50))
ax.set_xticklabels(np.arange(0, 301, 50), fontsize=14)
ax.set_ylim(0, 0.8)
ax.set_yticks(np.round(np.arange(0, 0.85, 0.2),1))
ax.set_yticklabels(np.round(np.arange(0, 0.85, 0.2),1), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'FT_DiffTR_Factor.pdf', format='pdf', bbox_inches='tight')

# UnSignalized + Diff turn ratio
df_Unsig_DiffTR = pd.read_csv(r'.\Unsig_DiffTR.att', sep =';')
UnSig_Diff_Factor = df_Unsig_DiffTR[['x12', 'x13', 'x21','x31']].values

fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(UnSig_Diff_Factor[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.1,$ $n_{1}=2$')
ax.plot(UnSig_Diff_Factor[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.1,$ $n_{1}=2$')
ax.plot(UnSig_Diff_Factor[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(UnSig_Diff_Factor[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$C_{b,m} = F_{b,m}(\vec{K}_t)/q_{b,t}$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 301)
ax.set_xticks(np.arange(0, 301,50))
ax.set_xticklabels(np.arange(0, 301, 50), fontsize=14)
ax.set_ylim(0, 0.8)
ax.set_yticks(np.round(np.arange(0, 0.85, 0.2),1))
ax.set_yticklabels(np.round(np.arange(0, 0.85, 0.2),1), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'Unsig_DiffTR_Factor.pdf', format='pdf', bbox_inches='tight')

# UnSignalized + Same turn ratio
df_Unsig_SameTR = pd.read_csv(r'.\Unsig_SameTR.att', sep =';')
UnSig_Diff_Factor = df_Unsig_SameTR[['x12', 'x13', 'x21','x31']].values
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(UnSig_Diff_Factor[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.2,$ $n_{1}=2$')
ax.plot(UnSig_Diff_Factor[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.2,$ $n_{1}=2$')
ax.plot(UnSig_Diff_Factor[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(UnSig_Diff_Factor[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$C_{b,m} = F_{b,m}(\vec{K}_t)/q_{b,t}$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 301)
ax.set_xticks(np.arange(0, 301,50))
ax.set_xticklabels(np.arange(0, 301, 50), fontsize=14)
ax.set_ylim(0, 0.8)
ax.set_yticks(np.round(np.arange(0, 0.85, 0.2),1))
ax.set_yticklabels(np.round(np.arange(0, 0.85, 0.2),1), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'Unsig_SameTR_Factor.pdf', format='pdf', bbox_inches='tight')


