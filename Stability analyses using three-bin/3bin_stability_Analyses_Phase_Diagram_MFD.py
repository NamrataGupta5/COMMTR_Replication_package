# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 18:27:55 2022
- Three-bin stability analyses to obtain phase diagrams and MFDs
- Generate figures 6-8 of the manuscript
- Make sure to change drive location to save necessary figure and data
@author: Namrata
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
is_ipython = 'inline' in matplotlib.get_backend()

class Bin_Env():
    '''Creates three-bin environment
    Takes parameters of TSC and bins as input
    Functions: MinGr, reset, Update_ModState, IsJam, GreenTime
    Get_BinVolume, Get_PhaseFlow, Get_AvgVolume, Get_AvgDensity,
    Is_Equilibrium, Stability_check, Derivatives'''
    def __init__(
                 self, policy = 'P0', kjam=150,FF=60,kc=40, PhaseNum=4, 
                 BinNum=3, CycTm =60,adaptivity= 0, delta = 0.001,
                  LaneArr=np.array([2,1,1]),
                 TurnRatio=np.array([0.1, 0.1, 0.2, 0.2]),
                 BinLenArr =np.array([1,1,1])
                 ):
        self.policy = policy
        self.BinNum = BinNum
        self.CycTm = CycTm
        self.kjam = kjam # Jam density
        self.FF = FF # Free flow speed
        self.kc = kc # Critical density
        self.w = self.FF*self.kc/(self.kjam-self.kc) #Back-propogation speed
        self.qm = self.kc*self.FF
        self.PhaseNum = PhaseNum # Number of phases
        self.LaneArr = LaneArr # Array of Number of lanes in bins
        self.BinLenArr = BinLenArr #Array of Length of bins
        self.TotLenArr = self.BinLenArr*self.LaneArr #Array of Total length of bins {ni*li}
        self.TotLen = sum(self.TotLenArr) #sum(ni*li) #Total network length
        self.state = 1e-4*np.ones(self.BinNum)
        self.ModState = np.array([self.state[0],self.state[0],self.state[1],self.state[2]])
        self.BLen = np.array([self.BinLenArr[0],self.BinLenArr[0],self.BinLenArr[1],self.BinLenArr[2]]) #For easy calculation
        self.BLane = np.array([self.LaneArr[0],self.LaneArr[0],self.LaneArr[1],self.LaneArr[2]]) #For easy calculation
        self.NetJam = False # Is network jammed
        self.adaptivity =adaptivity
        self.TurnRatio = TurnRatio
        self.BinFlowRate = 1e-8*np.ones(self.BinNum)
        self.Out_InFlow = 1e-8*np.ones((self.BinNum,self.BinNum))
        self.delta = delta
        self.GrTm = (CycTm/PhaseNum)*np.ones(PhaseNum)

    @property
    def MinGr(self): 
       '''Calculates minimum green time as per Eq. (29)'''
       return (1-self.adaptivity)/self.PhaseNum

    
    def reset(self):
        '''Reset initial state'''
        self.state = np.array([0,0,0], dtype=np.float32) #Starting from initial bin densities
        self.NetJam = False 
        self.ModState = self.Update_ModState(self.state)
        return np.array(self.ModState, dtype=np.float32)
       
    def Update_ModState(self, Density):
        '''For convinience'''
        ModDensity = np.array([Density[0],Density[0],Density[1],Density[2]])
        return ModDensity
            
    def IsJam(self):
        '''Checks if network is jammed. Uses Eq. 11b-11c'''
        if not((np.any((self.kjam-self.state[1:])>0.01)) and ((self.kjam-self.state[0])>0.01)): #Condition for jamming
            self.NetJam = True
    

    def GreenTime(self, ModDensity):
        '''Calculate green time for signal. Uses Eq. 27-28'''
        temp = ModDensity
        if self.policy == 'P0':
            GrTm = (self.MinGr+ (self.adaptivity*temp)/ max(1e-8,sum(temp)))
        
        elif self.policy == 'P1':
            if self.PhaseNum==4:
                k1,k11,k2 ,k3= temp
                p1, p2,p3,p4 = max(1e-8,k1-k2),max(1e-8,k1-k3),max(1e-8,k2-k1),max(1e-8,k3-k1) 
                p = np.array([p1,p2,p3,p4]) #Phase pressure
            GrTm = (self.MinGr+ (self.adaptivity*p)/sum(p))
        self.GrTm = GrTm
        return GrTm
        
    def Get_BinVolume(self, Density, GrTm):
        '''Give volume of each bin'''
        BV = np.zeros(self.BinNum)
        g = np.array([np.mean(GrTm[:2]),GrTm[2],GrTm[3]]) #Eq. 5-6; gi = avg(gij), j is lanes in bin i
        if not (self.NetJam): #if not jam
            for i in range(self.BinNum):
                if self.kjam-Density[i]>0.01: # For unjammed bins
                    BV[i] = min(self.FF*Density[i], self.qm*g[i], self.w*(self.kjam-Density[i]))
        self.BinFlowRate =BV
        return self.BinFlowRate
        
    
    def Get_PhaseFlow(self,Density, GrTm):
        '''Give outflow from each phase. Uses Eq. (9)'''
        ModDensity = self.Update_ModState(Density)

        BFR = self.Get_BinVolume(Density,GrTm) # Expected bin volume from given GrTm
   
        BV = np.array([self.BinFlowRate[0],self.BinFlowRate[0],
                              self.BinFlowRate[1],self.BinFlowRate[2]]) # For easy calculation. Since 3 bin model has 4 phase

        BV = BV*np.round(GrTm,2)/np.maximum(1e-8,np.round(GrTm,2))
        # PhaseFlow = np.minimum(TR*self.CycTm*BV*self.BLane/3600,ModDensity*self.BLen) #Outflow from in each phase
        # PhaseFlow = np.minimum(TR*BV*self.BLane,ModDensity*self.BLen) #Outflow from in each phase
        PhaseFlow = env.TurnRatio*BV*self.BLane #Outflow from in each phase
        self.Out_InFlow = 1e-8*np.ones((self.BinNum,self.BinNum)) # Array to stor inflow-outflow from bins

        self.Out_InFlow[0,1:]=PhaseFlow[:2] # Outflow from bin 1 is from phase 0 & 1
        self.Out_InFlow[1:,0]=PhaseFlow[2:] # Inflow in bin 1 is from phase 2 & 3

        # TO account from jammed bins
        JamInd = np.where(self.kjam-Density<0.01)[0] # FInd bins that are jammed
        for ind in JamInd:
            self.Out_InFlow[0,JamInd]=0 # Jammed bins cannot receive vehicles
            self.Out_InFlow[JamInd,0]=0 # Jammed bins cannot release vehicles
            self.Out_InFlow[JamInd,JamInd]=0 # Jammed bins cannot receive new vehicles
        return np.concatenate([self.Out_InFlow[0,1:],self.Out_InFlow[1:,0]])
                
    def Get_AvgVolume(self,BinVol):
        '''Gives average network volume'''
        return (BinVol @ self.TotLenArr)/self.TotLen
    
    def Get_AvgDensity(self,BinDens):
        '''Gives average network volume'''
        return (BinDens @ self.TotLenArr)/self.TotLen
    
    def IsEquilibrium(self,PhaseFlow):
        '''Checks if a given Phase Flow is matching eq. condition (Eq. 11(a))'''
        Equilibrium = False
        F12,F13,F21,F31 = PhaseFlow
        if abs(F12-F21) < 0.5 and abs(F13-F31) < 0.5: #Equilibrium condition; Eq. 11(a) 
            Equilibrium = True
        return Equilibrium
    
    def Stability_check(self, Flow_Derivative):
        '''Checks equilibrium nature for the derivative at equilibrium. 
        Uses Eq.(21) and (29)'''
        der12,der13,der21,der31 = Flow_Derivative
        trace = np.round(-((der12+der13)/(self.TotLenArr[0]) +\
                            der21/(self.TotLenArr[1]) +\
                            der31/(self.TotLenArr[2])),2) #Stability condition 1, Eq. (21)
        Det = np.round(der12*der31/(self.TotLenArr[0]*self.TotLenArr[2]) +\
                       der13*der21/(self.TotLenArr[0]*self.TotLenArr[1]) + \
                       der21*der31/(self.TotLenArr[1]*self.TotLenArr[2]),2) #Stability condition 2, Eq. (26)
        if trace < 0 and Det > 0: 
            Stablity = 1  #Stable Equ
        elif trace == 0 and Det == 0:
            Stablity = 2  #Neutral Eq
        else:
            Stablity = 0        #Unstable equ
        return Stablity

    def Derivatives(self,Equi_Density):
        '''Calculating system derivatives near equilibrium by calculating rate/
        of change in flow between two perturbed points near equilibrium'''
        Flow_Derivative = np.zeros(self.PhaseNum)
        for i in range(self.BinNum):
            if Equi_Density[i]==0:
                Der = self.FF
                if i == 0:
                    Flow_Derivative[0:2] = Der
                else:
                    Flow_Derivative[i+1] = Der

            else:
                k_plus = Equi_Density.copy()
                k_minus = Equi_Density.copy()
                k_plus[i] = Equi_Density[i] + self.delta # Perturbed point 1
                k_minus[i] = Equi_Density[i] - self.delta # Perturbed point 2
                GrTm_plus= self.GreenTime(self.Update_ModState(k_plus)) # Green time at Perturbed point 1
                GrTm_minus= self.GreenTime(self.Update_ModState(k_minus)) # Green time at Perturbed point 2
                Flow_petrurb_plus = self.Get_PhaseFlow(k_plus,GrTm_plus)   #Flow at Perturbed point 1
                Flow_petrurb_minus = self.Get_PhaseFlow(k_minus,GrTm_minus)  #Flow at Perturbed point 2
                # Calculating rate of change of flow at perturbed point 1 &2
                if i == 0:
                    Flow_Derivative[0] = 0.5*(Flow_petrurb_plus[0]-Flow_petrurb_minus[0])/self.delta 
                    Flow_Derivative[1] = 0.5*(Flow_petrurb_plus[1]-Flow_petrurb_minus[1])/self.delta 
                else:
                    Der = 0.5*(Flow_petrurb_plus[i+1]-Flow_petrurb_minus[i+1])/self.delta   
                    Flow_Derivative[i+1] = Der   
        return Flow_Derivative

FF, kc, kjam,PhaseNum, BinNum,CycTm=60,40,150,4, 3,60 #Basic parameters
Gamma = [0,1/3,1] # Adaptivity values
TurnRatio=np.array([0.1,0.1,0.2,0.2]) # Turn ratio
BinLenArr =np.array([1,1,1]) # Bin lengths
LaneArr=np.array([2,1,1])           # Number of lanes in rings
policy = ['P1','P0']

# policy = 'P1'
    
K = np.arange(0,kjam+0.01,1) # Density of bin 3
Congestion_Index = [1,2,3] # 1: q_I; 2: q_II; 3: q_III
SE = np.empty((10000000, BinNum,np.shape(Gamma)[0]))    #Empty array to store stable Eq
USE = np.empty((10000000, BinNum,np.shape(Gamma)[0]))   #Empty array to store unstable Eq
NE = np.empty((10000000, BinNum,np.shape(Gamma)[0]))   #Empty array to store Neutral Eq
MFD_SE = np.empty((10000000, 2,np.shape(Gamma)[0]))    #Empty array to store stable (AvgK, AvgQ)
MFD_USE = np.empty((10000000, 2,np.shape(Gamma)[0]))   #Empty array to store unstable (AvgK, AvgQ)
MFD_NE = np.empty((10000000, 2,np.shape(Gamma)[0]))   #Empty array to store Neutral (AvgK, AvgQ)
SE[:] = np.NaN
NE[:] = np.NaN
USE[:]= np.NaN
MFD_SE[:] = np.NaN
MFD_NE[:] = np.NaN
MFD_USE[:]= np.NaN
Is =0 #Index for stable equilibrium solution
Iu =0 #Index for unstable equilibrium solution  
In =0 #Index for neutral equilibrium solution
i = 0 #Index for gamma
delta=0.0001
c1 = 0

env= Bin_Env(policy, kjam, FF, kc, PhaseNum, BinNum, CycTm,Gamma[0],delta,
              LaneArr, TurnRatio, BinLenArr)
# pol=policy
for pol in policy:
    env.policy = pol
    for adaptivity in Gamma:
        env.adaptivity = adaptivity
        # env= Bin_Env(pol, kjam, FF, kc, PhaseNum, BinNum, CycTm,adaptivity,delta,
        #       LaneArr, TurnRatio, BinLenArr)
        for c1 in range(len(K)):
            k1 =K[c1]
            for c2 in range(c1):
                k2 = K[c2]
                ka = kc/PhaseNum 
                kb = kjam - (kjam-kc)*(1-adaptivity)/PhaseNum
    
                DensityTuples = [[k1,k1,k1],[k1,k2,k2],[k2,k1,k1],[k2,k1,k2],
                                 [k2,k2,k1],[k1,k2,k1],[k1,k1,k2]]     #Points satisfying equilibrium condition          
                if adaptivity == 0:
                    AddTuples = [[ka,ka,k1],[ka,k1,ka],[k1,ka,ka],
                                 [kb,kb,k1],[kb,k1,kb],[k1,kb,kb],
                                 [kb,ka,k1],[kb,k1,ka],[k1,kb,ka],
                                 [ka,kb,k1],[ka,k1,kb],[k1,ka,kb]] #Extra Points for fixed time
                elif 0<adaptivity<1:     
                    AddTuples =   [[kb,k1,k1],[k1,kb,k1],[k1,k1,kb],
                                   [kb,k1,kb],[k1,kb,kb],
                                   [kb,kb,k1]] #Extra Points for adaptive
                else:
                    AddTuples = []                
                DensityTuples = DensityTuples+AddTuples #Total points
                for Density in DensityTuples:
                    Density = np.array(Density)
                    ModDensity = env.Update_ModState(Density)
                    AvgK = env.Get_AvgDensity(Density)
                    if adaptivity == 0:
                        AddCond = not ((ka < Density[0] < kb) and (ka < Density[1] <kb) and (ka < Density[2]<kb))
                    else:
                        AddCond = True
                    if ((0 <=  AvgK <= kjam) and AddCond):
                        GrTm = env.GreenTime(ModDensity) #Green time at each point
                        PhaseFlow = env.Get_PhaseFlow(Density,GrTm) #Outflow at those point
                        if env.IsEquilibrium(PhaseFlow): # If the phase flow at equilibrium
                            Flow_Derivative= env.Derivatives(Density) #Derivatives at that point
                            Stability = env.Stability_check(Flow_Derivative) #Checking stability
                            BinVol = env.Get_BinVolume(Density, GrTm) #Avg volume at that point
                            AvgQ = env.Get_AvgVolume(BinVol)  #Avg Density at that point
    
                            if (Density[2] == kjam and Density[1]==kjam) or (Density[0]==kjam):   
                                SE[Is,:,i] = Density
                                AvgQ = 0
                                MFD_SE[Is,:,i] = [AvgK,AvgQ]
                                Is +=1 
                            else:
    
                                if Stability ==1:
                                    #Stable Equi
                                    SE[Is,:,i] = Density
                                    MFD_SE[Is,:,i] = [AvgK,AvgQ]
                                    Is +=1
                                elif Stability == 0:
                                    #Unstable Eq
                                    USE[Iu,:,i] = Density
                                    MFD_USE[Iu,:,i] = [AvgK,AvgQ]
                                    Iu +=1
                                else:
                                    #Neutral Eq
                                    NE[In,:,i] = Density
                                    MFD_NE[In,:,i] = [AvgK,AvgQ]
                                    In +=1  
        i+=1
    
    
    K3 = np.arange(0,kjam+1,10) # Density of bin 3   
    i=0
    for gam in Gamma:                     
        for k3 in K3:
            for k2 in K3:
                for k1 in K3:   
                    Sol_set = np.array([k1,k2,k3])
                    AvgK = env.Get_AvgDensity(Sol_set)
                    ModDensity = env.Update_ModState(Sol_set)
                    GrTm = env.GreenTime(ModDensity) 
                    if 0 <= AvgK <= kjam:
                        if (k3 == kjam and k2==kjam) or (k1==kjam):                               
                            SE[Is,:,i] = Sol_set
                            AvgQ = 0
                            MFD_SE[Is,:,i] = [AvgK,AvgQ]
                            Is +=1
        i+=1
    
          
    ##### Writing File and Data manipulation for P0
    FileLoc = r'C:\Users\admin\OneDrive - IIT Bombay\COMMTR_3bin\Replication Package\Stability analyses'    
    frames = []
    MFD_frames = []
    for i in range(len(Gamma)):
        Sdf = pd.DataFrame(SE[:,:,i], columns=['k1','k2','k3']).dropna()
        Sdf['Equilibrium Type']='Stable'
        Udf = pd.DataFrame(USE[:,:,i], columns=['k1','k2','k3']).dropna()
        Udf['Equilibrium Type']='Unstable'
        Ndf = pd.DataFrame(NE[:,:,i], columns=['k1','k2','k3']).dropna()
        Ndf['Equilibrium Type']='Neutral'
        df = pd.concat([Sdf,Udf,Ndf])
        df['Gamma'] = Gamma[i]
        frames.append(df)
        
        MFD_Sdf = pd.DataFrame(MFD_SE[:,:,i], columns=['AvgK','AvgQ']).dropna()
        MFD_Sdf['Equilibrium Type']='Stable'
        MFD_Udf = pd.DataFrame(MFD_USE[:,:,i], columns=['AvgK','AvgQ']).dropna()
        MFD_Udf['Equilibrium Type']='Unstable'
        MFD_Ndf = pd.DataFrame(MFD_NE[:,:,i], columns=['AvgK','AvgQ']).dropna()
        MFD_Ndf['Equilibrium Type']='Neutral'
        MFD_df = pd.concat([MFD_Sdf,MFD_Udf,MFD_Ndf])
        MFD_df['Gamma'] = Gamma[i]
        MFD_frames.append(MFD_df)
    FullDf = pd.concat(frames)
    FileName = os.path.join(FileLoc,pol +'_PhaseDia_Final.att')
    FullDf.to_csv(FileName, sep=';',index = False)
    
    MFD_FullDf = pd.concat(MFD_frames)
    FileName = os.path.join(FileLoc, pol +'_MFD_Final.att')
    MFD_FullDf.to_csv(FileName, sep=';',index = False)
    
    #### Plotting 
    def set_size(width, fraction=1, subplot=[1, 1]):
        if width == 'elsevier':
            width_pt = 468.
        elif width == 'beamer':
            width_pt = 307.28987
        else:
            width_pt = width
        fig_width_pt = width_pt * fraction      # Width of figure
        inches_per_pt = 1 / 72.27               # Convert from pt to inches
        golden_ratio = 0.75                     # (5**.5 - 1) / 2
        fig_width_in = fig_width_pt * inches_per_pt  # Figure width in inches
        fig_height_in = fig_width_in * golden_ratio * (subplot[0] / subplot[1])
        fig_dim = (fig_width_in, fig_height_in)
        return fig_dim
    
    # Using seaborn's style
    plt.style.use('seaborn-colorblind')  
    
    nice_fonts = {
            # "text.usetex": True,
            "font.family": 'Times New Roman',
            "axes.labelsize": 14,
            "font.size": 14,
            "legend.fontsize": 14,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
    }
    
    plt.rcParams.update(nice_fonts)
    
    Marker = ['s','o','v',',','d','v']
    MarkerSize = [20,30,40,30,30]
    i=0
    for g in Gamma:   
        fig = plt.figure(figsize =(8,7))
        ax = plt.axes(projection ="3d")
        xs = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Stable')]['k1'].values
        ys = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Stable')]['k2'].values
        zs = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Stable')]['k3'].values
        xu = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Unstable')]['k1'].values
        yu = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Unstable')]['k2'].values   
        zu = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Unstable')]['k3'].values  
        xn = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Neutral')]['k1'].values
        yn = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Neutral')]['k2'].values   
        zn = FullDf[(FullDf['Gamma']==g) & (FullDf['Equilibrium Type']=='Neutral')]['k3'].values   
        ax.scatter3D(xs, ys, zs,color='g',label='Stable', marker= Marker[0],s=MarkerSize[0],
                    facecolors='none', edgecolors='g',linewidths=0.5)
        ax.scatter3D(xu, yu, zu, color='r',label='Unstable', marker= Marker[1],
                    s=MarkerSize[1],facecolors='none', edgecolors='r',linewidths=0.5)
        ax.scatter3D(xn, yn,zn, color='k',label='Neutral', marker= Marker[2],
                    s=MarkerSize[2],facecolors='none', edgecolors='k',linewidths=0.5)
        ax.set_xlabel('$k_1$ $(Veh/km)$')
        ax.set_ylabel('$k_2$ $(Veh/km)$')
        ax.set_zlabel('$k_3$ $(Veh/km)$')
        ax.set_ylim(0, 160)
        ax.set_xlim(0, 160)
        ax.set_zlim(0, 160)
        ax.set_xticks(np.arange(0, 161, 20))
        ax.set_yticks(np.arange(0, 161, 20))
        ax.set_zticks(np.arange(0, 161, 20))
        ax.set_xticklabels(np.arange(0, 161, 20), fontsize=14)
        ax.set_yticklabels(np.arange(0, 161, 20), fontsize=14)
        ax.set_zticklabels(np.arange(0, 161, 20), fontsize=14)
        ax.legend()
        plt.tight_layout()
        FileName = os.path.join(FileLoc,pol +'_PhaseDia_'+str(np.round(g,1))+'.png')
        plt.savefig(FileName, format='png', bbox_inches='tight')
        FileName = os.path.join(FileLoc,pol +'_PhaseDia_'+str(np.round(g,1))+'.pdf')
        plt.savefig(FileName, format='pdf', bbox_inches='tight')    
    
        fig = plt.figure(figsize =(8,7))
        ax = plt.axes()
        xs = MFD_FullDf[(MFD_FullDf['Gamma']==g) & (MFD_FullDf['Equilibrium Type']=='Stable')]['AvgK'].values
        ys = MFD_FullDf[(MFD_FullDf['Gamma']==g) & (MFD_FullDf['Equilibrium Type']=='Stable')]['AvgQ'].values
        xu = MFD_FullDf[(MFD_FullDf['Gamma']==g) & (MFD_FullDf['Equilibrium Type']=='Unstable')]['AvgK'].values
        yu = MFD_FullDf[(MFD_FullDf['Gamma']==g) & (MFD_FullDf['Equilibrium Type']=='Unstable')]['AvgQ'].values   
        xn = MFD_FullDf[(MFD_FullDf['Gamma']==g) & (MFD_FullDf['Equilibrium Type']=='Neutral')]['AvgK'].values
        yn = MFD_FullDf[(MFD_FullDf['Gamma']==g) & (MFD_FullDf['Equilibrium Type']=='Neutral')]['AvgQ'].values   
        ax.scatter(xs, ys,color='g',label='Stable', marker= Marker[0],s=MarkerSize[0],
                    facecolors='none', edgecolors='g',linewidths=0.7)
        ax.scatter(xu, yu,color='r',label='Unstable', marker= Marker[1],
                    s=MarkerSize[1],facecolors='none', edgecolors='r',linewidths=0.7)
        ax.scatter(xn, yn,color='k',label='Neutral', marker= Marker[2],
                    s=MarkerSize[2],facecolors='none', edgecolors='k',linewidths=0.7)
        ax.set_xlabel('$\overline{K}$ $(Veh/km)$')
        ax.set_ylabel('$\overline{Q}$ $(Veh/hr)$')
        ax.set_ylim(0, 800)
        ax.set_xlim(0, 160)
        ax.set_xticks(np.arange(0, 161, 20))
        ax.set_yticks(np.arange(0, 850, 100))
        ax.set_xticklabels(np.arange(0, 161, 20), fontsize=14)
        ax.set_yticklabels(np.arange(0, 850, 100), fontsize=14)
        ax.legend()
        plt.tight_layout()
        FileName = os.path.join(FileLoc,pol +'_MFD_'+str(np.round(g,1))+'.png')
        plt.savefig(FileName, format='png', bbox_inches='tight')
        FileName = os.path.join(FileLoc,pol +'_MFD_'+str(np.round(g,1))+'.pdf')
        plt.savefig(FileName, format='pdf', bbox_inches='tight')
        plt.close('all')     
