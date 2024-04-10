# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 19:07:46 2022
Plotting data for 3bin model

@author: admin
"""

import glob, os, shutil
os.chdir(r'D:\Vissim_models\Ring Models\3ring Model_APS_TGF\LinkFlow_Vs_GrTm\L1_1000_R_1')

import math
import pandas as pd
import numpy as np
import warnings
import PySimpleGUI as sg
import re
from itertools import repeat

import random
import matplotlib.pyplot as plt
from time import time
from datetime import datetime
import matplotlib
from collections import namedtuple

def get_moving_average(period, values):
    '''Moving average of given array using given period'''
    if len(values) >= period:
        df = pd.DataFrame(values,columns=['val']) #Calculation using dataframe is easier
        moving_avg = df['val'].rolling(period).mean().fillna(0).values
    else:
        moving_avg = np.zeros(len(values))
    return moving_avg

def plot(values, moving_avg_period, title = 'Moving Average...', ylabel='Duration'):
    '''For ploting moving average'''
    plt.figure(2)
    plt.clf()        
    # plt.title(title)
    YLabel = ylabel +' (Moving Average of 100 episodes)'
    plt.xlabel('Episode')
    plt.ylabel(YLabel)
    # plt.plot(values)

    moving_avg = get_moving_average(moving_avg_period, values)
    plt.plot(moving_avg)    
    plt.pause(0.001)
    print("Episode", len(values), "\n", \
        moving_avg_period, "episode moving avg:", moving_avg[-1])
    
def MFD_plot(env, PhNum, AvgDen,AvgVol, moving_avg_period,agent, color, marker):
    '''For plotting MFD'''
    moving_avg_Den = get_moving_average(moving_avg_period, AvgDen)
    moving_avg_Vol = get_moving_average(moving_avg_period, AvgVol)
    fig = plt.figure(figsize =(8,7))
    ax = plt.axes()
    ax.scatter(moving_avg_Den, moving_avg_Vol, color=color,label=agent, marker= marker,s=20,
                facecolors='none', edgecolors=color,linewidths=0.5)
    ax.set_xlabel('$K$ $(Veh/km)$')
    ax.set_ylabel('$Q$ $(Veh/hr)$')
    ax.set_xlim(0, int(env.kjam+10))
    ax.set_ylim(0, int(env.qm/PhNum+100))
    ax.set_xticks(np.arange(0, int(env.kjam+11), 20))
    ax.set_yticks(np.arange(0, int(env.qm/PhNum+101), 200))
    ax.set_xticklabels(np.arange(0, int(env.kjam+11), 20), fontsize=14)
    ax.set_yticklabels(np.arange(0, int(env.qm/PhNum+101), 200), fontsize=14)
    plt.legend()
    
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
FT_SameTR_Outflow = df_FT_SameTR[['F12', 'F13', 'F21','F31']].values
FT_SameTR_Factor = df_FT_SameTR[['x12', 'x13', 'x21','x31']].values
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(FT_SameTR_Outflow[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.2,$ $n_{1}=2$')
ax.plot(FT_SameTR_Outflow[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.2,$ $n_{1}=2$')
ax.plot(FT_SameTR_Outflow[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(FT_SameTR_Outflow[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$F_{b,m}(\vec{K}_t) \, (Veh/hr)$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 301)
ax.set_xticks(np.arange(0, 301, 50))
ax.set_xticklabels(np.arange(0, 301, 50), fontsize=14)
ax.set_ylim(0, 210)
ax.set_yticks(np.arange(0, 210, 50))
ax.set_yticklabels(np.arange(0, 210, 50), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'.\Figures\FT_SameTR_Out.pdf', format='pdf', bbox_inches='tight')

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
plt.savefig(r'.\Figures\FT_SameTR_Factor.pdf', format='pdf', bbox_inches='tight')

# Signalized + Diff turn ratio
df_FT_DiffTR = pd.read_csv(r'.\FT_DiffTR.att', sep =';')
FT_DiffTR_Outflow = df_FT_DiffTR[['F12', 'F13', 'F21','F31']].values
FT_Diff_Factor = df_FT_DiffTR[['x12', 'x13', 'x21','x31']].values
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(FT_DiffTR_Outflow[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.1,$ $n_{1}=2$')
ax.plot(FT_DiffTR_Outflow[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.1,$ $n_{1}=2$')
ax.plot(FT_DiffTR_Outflow[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(FT_DiffTR_Outflow[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$F_{b,m}(\vec{K}_t) \, (Veh/hr)$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 401)
ax.set_xticks(np.arange(0, 401, 50))
ax.set_xticklabels(np.arange(0, 401, 50), fontsize=14)
ax.set_ylim(0, 210)
ax.set_yticks(np.arange(0, 210, 50))
ax.set_yticklabels(np.arange(0, 210, 50), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'.\Figures\FT_DiffTR_Out.pdf', format='pdf', bbox_inches='tight')

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
plt.savefig(r'.\Figures\FT_DiffTR_Factor.pdf', format='pdf', bbox_inches='tight')

# UnSignalized + Diff turn ratio
df_Unsig_DiffTR = pd.read_csv(r'.\Unsig_DiffTR.att', sep =';')
UnSig_DiffTR_Outflow = df_Unsig_DiffTR[['F12', 'F13', 'F21','F31']].values
UnSig_Diff_Factor = df_Unsig_DiffTR[['x12', 'x13', 'x21','x31']].values
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(UnSig_DiffTR_Outflow[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.1,$ $n_{1}=2$')
ax.plot(UnSig_DiffTR_Outflow[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.1,$ $n_{1}=2$')
ax.plot(UnSig_DiffTR_Outflow[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(UnSig_DiffTR_Outflow[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$F_{b,m}(\vec{K}_t) \, (Veh/hr)$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 301)
ax.set_xticks(np.arange(0, 301, 50))
ax.set_xticklabels(np.arange(0, 301, 50), fontsize=14)
ax.set_ylim(0, 210)
ax.set_yticks(np.arange(0, 210, 50))
ax.set_yticklabels(np.arange(0, 210, 50), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'.\Figures\Unsig_DiffTR_Out.pdf', format='pdf', bbox_inches='tight')

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
plt.savefig(r'.\Figures\Unsig_DiffTR_Factor.pdf', format='pdf', bbox_inches='tight')

# UnSignalized + Same turn ratio
df_Unsig_SameTR = pd.read_csv(r'.\Unsig_SameTR.att', sep =';')
UnSig_DiffTR_Outflow = df_Unsig_SameTR[['F12', 'F13', 'F21','F31']].values
UnSig_Diff_Factor = df_Unsig_SameTR[['x12', 'x13', 'x21','x31']].values
fig, ax = plt.subplots(1, 1,figsize =(8,7))
ax.plot(UnSig_DiffTR_Outflow[:,0],color='r', linestyle='-', linewidth= 2, label=r'$T_{1,2}=0.2,$ $n_{1}=2$')
ax.plot(UnSig_DiffTR_Outflow[:,1],color='b', linestyle='-', linewidth= 2, label=r'$T_{1,3}=0.2,$ $n_{1}=2$')
ax.plot(UnSig_DiffTR_Outflow[:,2],color='g', linestyle='-', linewidth= 2, label=r'$T_{2,1}=0.2,$ $n_{2}=1$')
ax.plot(UnSig_DiffTR_Outflow[:,3],color='k', linestyle='-', linewidth= 2, label=r'$T_{3,1}=0.2,$ $n_{3}=1$')
ax.set_ylabel(r'$F_{b,m}(\vec{K}_t) \, (Veh/hr)$')
ax.set_xlabel('Timestep')
ax.set_xlim(0, 301)
ax.set_xticks(np.arange(0, 301, 50))
ax.set_xticklabels(np.arange(0, 301, 50), fontsize=14)
ax.set_ylim(0, 210)
ax.set_yticks(np.arange(0, 210, 50))
ax.set_yticklabels(np.arange(0, 210, 50), fontsize=14)
ax.legend()
fig.tight_layout()
plt.savefig(r'.\Figures\Unsig_SameTR_Out.pdf', format='pdf', bbox_inches='tight')

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
plt.savefig(r'.\Figures\Unsig_SameTR_Factor.pdf', format='pdf', bbox_inches='tight')

#RingFD
df_RingFD = pd.read_csv(r'.\L1000_RingFD.att', sep =';')
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
plt.savefig(r'.\Figures\RingFD.pdf', format='pdf', bbox_inches='tight')

#g = 1/3
df_0_40_10_10 = pd.read_csv(r'.\L1000_C60_0_40_10_10.att', sep =';')

#g =1/4
df_10_20_15_15 = pd.read_csv(r'.\L1000_C60_10_20_15_15.att', sep =';')
df_15_15_15_15 = pd.read_csv(r'.\L1000_C60_15_15_15_15.att', sep =';')
df_0_30_15_15 = pd.read_csv(r'.\L1000_C60_0_30_15_15.att', sep =';')

#g = 1/6
df_5_15_20_20 = pd.read_csv(r'.\L1000_C60_5_15_20_20.att', sep =';')
df_10_10_20_20 = pd.read_csv(r'.\L1000_C60_10_10_20_20.att', sep =';')
df_0_20_20_20 = pd.read_csv(r'.\L1000_C60_0_20_20_20.att', sep =';')
df_20_0_20_20 = pd.read_csv(r'.\L1000_C60_20_0_20_20.att', sep =';')
df_20_20_10_10 = pd.read_csv(r'.\L1000_C60_20_20_10_10.att', sep =';')
df_10_30_10_10 = pd.read_csv(r'.\L1000_C60_10_30_10_10.att', sep =';')

#g=1/3
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
plt.savefig(r'.\Figures\BinFlow_GrTm1.pdf', format='pdf', bbox_inches='tight')

#g=1/4
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
plt.savefig(r'.\Figures\BinFlow_GrTm2.pdf', format='pdf', bbox_inches='tight')


#g=1/6
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
plt.savefig(r'.\Figures\BinFlow_GrTm3.pdf', format='pdf', bbox_inches='tight')




