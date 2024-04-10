# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 15:48:44 2023
- Please make sure to change directory location
Input: 1) Vissim files and directory
       2) Basic simulation parameters
            FFSpd --> Free flow speed
            EpDur --> Simulation duration
            SimRes --> Simulation resolution
            RandNo --> Random seed number. Changes for multiple repetitions
            EvalFromTm --> Time when network parameter start recording
            EvalInter --> Aggregation inverval for result
            CycTm --> Cycle time
            EvalVar --> Variables that need to be recorded in vissim
            Quickmode, VehVisualization --> Setting in vissim for faster simulations

       3) network parameters
            SC --> Array of signal controllers
            SG --> Array of signal groups 
            InLinks --> Array of incoming links numbers. Map it with signal group of each signal controller
            ExLinks_st --> Array of exiting links numbers for through movements. Map according to InLinks
            ExLinks_TR --> Array of exiting links numbers for turning movements. Map according to InLinks
            TR --> Array of turn ratios
            ST --> Array of ratio of vehicles going straight
    
-Important Points!
    - Make sure that in vissim the link segment data is per lane
    - Now, extraction of parameter by using 'Avg:LinkEvalSegs\Density(Current,Last,All)' gives avg density of the link,
    so, if ring1 lane1 density is k11 & lane 2 density is k22. The command gives 0.5*(k11+k12)
    - Now length column is multiplied by lanes and then we do ki*li calculation;
    - essentially, we will get AvgK = (0.5*(k11+k12)*(2*l1)+(k2)*(l2)+(k3)*(l3))/(2*l1+l2+l3)
    - R1k = (0.5*(k11+k12)*(2*l1))/(2*l1)
@author: Namrata
"""

import pandas as pd
import numpy as np
import PySimpleGUI as sg
import re
import warnings
import win32com.client as com
import os, shutil
import matplotlib.pyplot as plt
import matplotlib

is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython: from IPython import display

os.chdir(r'C:\Users\admin\OneDrive - IIT Bombay\COMMTR_3bin\Replication Package\Grid network simulation\Net_2cross2')

warnings.simplefilter(action='ignore', category=FutureWarning)

class VisEnv():
    def __init__(
                 self,Vissim,VFile, SHdf, MFD_df,EpDur,BaseDir,EvalVar,
                 SimRes=3, CycTm =60,EvalFromTm = 0,EvalInter=60, 
                 FFSpd = 30
                 ):
        
        self.Vissim = Vissim
        self.VFile = VFile
        self.EpDur = EpDur
        self.EpCount = EpDur
        self.SHdf = SHdf
        self.MFD_df = MFD_df
        self.Net = Vissim.Net
        self.Sim = Vissim.Simulation
        self.Eval = Vissim.Evaluation
        self.Graph = Vissim.Graphics.CurrentNetworkWindow
        self.LinkObj = self.Net.Links
        self.VehObj = self.Net.Vehicles
        self.SimRes = SimRes
        self.CycTm = CycTm
        self.IntArr = self.SHdf['SC'].unique()
        self.TotInt = len(self.IntArr)
        self.PhArr = self.SHdf['SG'].unique()
        self.PhNum = len(self.PhArr)
        self.TotPhNum = self.SHdf.shape[0]
        self.ResDir = None
        self.EvalVar = EvalVar
        self.EvalFromTm = EvalFromTm
        self.EvalInter = EvalInter
        self.FFSpd = FFSpd
        self.TotLen = None # Total network length including connector
        self.RandNo = 41
        self.RunNo = 0
        self.BaseDir = BaseDir        
        
        
    def InVisSet(self):
        '''Sets initial values in vissim'''
        self.Sim.SetAttValue('SimPeriod',self.EpDur+1) #episode duration
        self.Sim.SetAttValue('SimRes',self.SimRes) #sim resolution
        self.Eval.SetAttValue('EvalOutDir',self.ResDir)
        Parameter = ['CollectData','FromTime','ToTime','Interval'] #eval conf
        ParValues = [1,self.EvalFromTm,self.EpDur,self.EvalInter]
        for V in self.EvalVar:
            count = 0
            for P in Parameter:
                PV = ParValues[count]
                self.Eval.SetAttValue(''.join([V,P]),PV)
                self.Vissim.Evaluation.SetAttValue(''.join([V,P]),PV)
                count +=1
   
    def reset(self, QuickMode = 1, VehVisualization = 0):
        '''Reset Vissim and redefine vissim related variables'''
        self.EpCount = self.EpDur
        self.Sim.SetAttValue('RandSeed', self.RandNo) #Random seed change in vissim   
        self.Graph.SetAttValue("QuickMode",QuickMode)
        self.Graph.SetAttValue("VehVisualization",VehVisualization)


                
    def SingleStep(self):
        '''Run 1 sec in simulation'''
        for i in range(self.SimRes):
            self.Sim.RunSingleStep()  # Runs 1 step
    
    def State(self):
        '''Retrieve parameters from vissim, Update densities in SHdf, 
        Calculate average network parameters of current simulation and evaluation interval'''
        # LinkObj = Net.Links
        RelAtt = ['No','NumLanes','Length2D',
                  'Avg:LinkEvalSegs\Density(Current,Last,All)',
                  'Avg:LinkEvalSegs\Volume(Current,Last,All)',
                  'Avg:LinkEvalSegs\Speed(Current,Last,All)']  # Parameters to be extracted from Vissim
        values = self.LinkObj.GetMultipleAttributes(RelAtt)    # Vissim Extraction
        col = ['Link','Lanes','Length','Density','Volume','Speed']
        df = pd.DataFrame(values,columns= col, dtype = np.float32) # Storing vissim parameters in df
        df.fillna(0,inplace = True)         #Data cleaning
        temp = df['Speed']
        for i in range(len(temp)):
            if temp[i] == '':
                temp[i] = self.FFSpd
            else:
                temp[i] = float(temp[i])
        df['Speed'] = temp
        df['Volume'] = df['Volume'].div(df['Lanes'], axis = 'index').values
        df['Density'] = df['Density'].div(df['Lanes'], axis = 'index').values
        df['Speed'] = df['Speed'].div(df['Lanes'], axis = 'index').values
        x = self.SHdf.copy()
        Col = np.array(['InLinks', 'ExLinks_st', 'ExLinks_TR'])
        for iterator in df.itertuples():
            LinkNo = iterator.Link
            DensityVal = iterator.Density
            for c in Col:
                ind = x[x[c]==LinkNo].index
                x.loc[ind,'K_'+c]=DensityVal
        self.SHdf = x.sort_index().copy() # Resorting by index
    
    def GreenTm(self, gamma,policy):
        '''Calculate Green time for policy P0, and P1'''

        g = self.CycTm/self.PhNum
        MinGr = (1-gamma)*g       # Minimum green time
        
        # GrTm = g*np.ones(PhNum) # Array to store green time
        MaxGr = self.CycTm - (self.PhNum -1)*MinGr    # Maximum green time    
        if gamma == 0:
            self.SHdf['GrTm'] = g # Fixed-Time signal controller
        else: 
            GrTm = np.zeros(self.TotPhNum)
            ind = 0
            for sc in self.IntArr:
                df = self.SHdf[self.SHdf['SC']==sc]
                Xin = df['K_InLinks'].values  # Revisit on this facor 2
                
                if 'P1' in policy:
                    Xout = 0.2*df['K_ExLinks_TR'].values +0.8*df['K_ExLinks_st'].values # Revisit the summation
                    Press = np.maximum(1e-5,Xin-Xout)  # np.aximum allows comparison of 2 arrays
                    if sum(Press) <5e-5:
                        x = np.where(Xin-Xout==min(Xin-Xout))[0]
                        Press[x] = 100
                    GrTm_temp = Press*gamma*self.CycTm/sum(Press) +MinGr*np.ones(self.PhNum) # MinGr +gamma*CycTm*(pi)/sum(pi)
                elif 'P0' in policy:
                    Press = np.maximum(1e-5,Xin)
                    GrTm_temp = Press*gamma*self.CycTm/sum(Press) +MinGr*np.ones(self.PhNum) # MinGr +gamma*CycTm*(ki)/sum(ki)
                GrTm_temp = np.array(GrTm_temp, dtype = np.float32)
                GrTm[ind:ind+4] = np.round(GrTm_temp)
                ind += 4
            self.SHdf['GrTm'] = GrTm
        
    def RunCycle(self):
        '''Run one signal cycle. Updates signals for each intersection after each sec.'''
        ActPhArr = np.zeros(self.TotInt, dtype = np.int8) # Starting from phase 1 at all intersections, since no offset
        GCountArr = self.SHdf[self.SHdf['SG']==1]['GrTm'].values # Phase 1 green time
        CycCount = self.CycTm # Cycle time counter
        if self.EpCount == self.EpDur:
            self.SingleStep()  # Signal can't be changed before simulation start
            GCountArr = GCountArr-1 
            CycCount-=1
            self.EpCount-=1
        while(CycCount):
            if self.EpCount == 0:
                break
            else:
                for i in range(len(self.IntArr)):
                    SC = self.SC_Arr[i]         #For each intersection
                    SigStat = ['RED' for i in range(len(self.PhArr))] #All red
                    if GCountArr[i]>0: # If active phase has remaining green time
                        GCountArr[i] -= 1 # Reduce the green time
                    else:
                        if ActPhArr[i] < self.PhNum-1: 
                            ActPhArr[i] +=1       # Next phase becomes active
                            GCountArr[i] = self.SHdf[(self.SHdf['SG']==ActPhArr[i]+1) & 
                                                     (self.SHdf['SC']==i+1)]['GrTm'].values[0] # Gcounter = Next phase green time
                            GCountArr[i] -=1    # Since actuation happens after this counter is reduced after this
                        else:
                            ActPhArr[i] = 0    
                    SigStat[ActPhArr[i]] = 'GREEN'  # Active phase becomes green
                    SigDict = dict(zip(self.PhArr,SigStat)) 
                    SC.SGs.SetMultiAttValues('State',tuple(SigDict.items()))   #Update signal timing
                self.SingleStep()  #Run one step
                CycCount-=1       #Update cycle counter
                self.EpCount-=1        #Update Episode counter
                

    def LinkEval(self, policy, gamma):
        '''Calculates df for link-wise parameters,'''
        NumofInt = int((self.EpDur -self.EvalFromTm)/self.EvalInter) # Number of intervals

        col = ['Interval','Avg:LinkEvalSegs\Density', 'Avg:LinkEvalSegs\Speed', 
               'Avg:LinkEvalSegs\Volume','NumLanes', 'Length2D','No','IsConn'] #Avg:LinkEvalSegs\ gives avg link parameter (avg in interval & avg in lanes)
                                                                # Works when vissim collects per lane data
        dfcol = [re.findall(r"[\w']+", col[i])[-1] \
                        for i in range(0,len(col),1)] #data frame column names
        EvalDf_Avg = pd.DataFrame(columns = ['Interval','AvgK','AvgQ','AvgS'],
                      index = np.arange(1, NumofInt +1, 1)) #initialized evaluation df
        index = 0
        for i in range(NumofInt):
            index = i+1
            st_tm = self.EvalFromTm + (i)*self.EvalInter #start time of interval i
            ed_tm = st_tm + self.EvalInter #end time of interval i
            RelAtt = [] # parameters requiring extraction from vissim
            for j in range(1,len(col),1):
                if col[j] in ['Length2D','No', 'NumLanes','IsConn']:
                    RelAtt.append(col[j])
                else:
                    att = ''.join([col[j],"(",str(self.RunNo),',',str(index),",all)"])
                    RelAtt.append(att)
            values = self.LinkObj.GetMultipleAttributes(RelAtt) #values extracted from vissim
            df = pd.DataFrame(values,columns= dfcol[1:], dtype = np.float32) #data frame from values
            df.fillna(0,inplace = True) # removing Nan
            df = df.replace([''],str(self.FFSpd)) #'' comes only for speed column when there is no vehicle on the link;
                                                  # essentially link is in free-flow
            sym = ['K','Q','S']
            var = ['Density','Volume','Speed']
            
            Method = "_".join([policy, 'G',str(gamma)]) #Converting vehicle input to string
            for VS,VN in zip(sym,var):
                # VSmulL = '{}mulL'.format(VS) #e.g. 'KmulL'
                EvalDf_Avg.at[index,'Avg{}'.format(VS)]= np.round(df[VN].mul(df['Length2D'], axis = 'index').sum()/self.TotLen,2)  #Variable*D
                EvalDf_Avg.at[index,'Interval'] = '_'.join([str(st_tm),str(ed_tm)]) #interval e.g. 0_60
            FlName = '_'.join([Method,'Avgdf',VS,str(self.RandNo)])  #e.g. BP_35_35
            AggResultFl = os.path.join(self.ResDir,''.join([FlName,'.att'])) #path of result file
            EvalDf_Avg.to_csv(AggResultFl, sep=';',index = False) #storing csv file
        return EvalDf_Avg, Method

class Experiment():
   def __init__(self,env, policy, gamma,BaseDir,
                Repeat=5, RandNo_st=42,
                QuickMode = 1, VehVisualization = 0):
        self.env = env               
        self.Repeat = Repeat
        self.RandNo_st = RandNo_st
        self.policy = policy
        self.gamma = gamma
        self.BaseDir = BaseDir
        self.RunNo_st = 1
        self.QuickMode = QuickMode
        self.VehVisualization = VehVisualization

   def ExpInitialize(self):
        '''Initialize Experiment'''
        DirName = '_'.join([self.policy, str(self.gamma)])
        ResDir = os.path.join(self.BaseDir, DirName) #to store results of current exp
        while os.path.exists(ResDir): #ensuring that DirPath doesn't pre-exist 
            DirName = '_'.join([DirName,str(1)])
            ResDir = os.path.join(self.BaseDir, DirName)
        os.mkdir(ResDir) #Creating new directory (eg: NormQ_200_1...)to store results of current exp
        self.env.ResDir = ResDir
        self.env.Vissim.LoadNet(self.env.VFile)
        self.env.Net = self.env.Vissim.Net
        self.env.Sim = self.env.Vissim.Simulation
        self.env.Graph = self.env.Vissim.Graphics.CurrentNetworkWindow
        self.env.Eval = self.env.Vissim.Evaluation
        self.env.LinkObj = self.env.Net.Links
        self.env.VehObj = self.env.Net.Vehicles
        self.env.SC_Arr = self.env.Net.SignalControllers.GetAll
        self.env.TR_Object =  self.env.Net.VehicleRoutingDecisionsStatic.GetAll
        self.env.Route_Ring_TR = [t.VehRoutSta for t in self.env.TR_Object]
        self.env.RandNo = self.RandNo_st
        self.env.RunNo = self.RunNo_st
        self.env.InVisSet()
        if self.env.TotLen == None:
            RelAtt = ['No','Length2D','IsConn','NumLanes']
            values = self.env.LinkObj.GetMultipleAttributes(RelAtt)
            col = ['Link','Length','IsConn','Lanes']
            dfl = pd.DataFrame(values,columns= col, dtype = np.float32)
            self.env.LinkArr = np.arange(1,61,1)
            self.env.TotLen = np.round(dfl['Length'].mul(dfl['Lanes'], axis = 'index').sum())


                      
   def RunExp(self):
        '''Run Experiment'''
        for r in range(self.Repeat):
            self.env.reset(self.QuickMode,self.VehVisualization)   # Set basic parameters in vissim

            if self.env.EpCount == self.env.EpDur:
                self.env.SingleStep()       # Signals cannot be set without starting simulation
            self.env.EpCount-=1 
               
            
            while(self.env.EpCount): 
                # AvgK,AvgQ,AvgS = self.env.State()
                self.env.State()
                if self.policy in ['P1','P0']:                                                                  
                    self.env.GreenTm(self.gamma,self.policy)  # Signalized intersection, green time is calculated each cycle
                    self.env.RunCycle()
                else:                                               # Unsiganlized intersection; All approaches are green
                    self.env.SingleStep()
                    self.env.EpCount-=1 
            self.env.Sim.stop()
 
            EvalDf,Method = self.env.LinkEval(self.policy, self.gamma)
            plotting(self.env.RandNo,self.env.ResDir, Method,EvalDf, MovAvgWin = 15)   
            if self.env.RunNo == self.Repeat:
                self.env.RunNo = 'Avg'
                self.env.RandNo = 'Avg'
                EvalDf,Method = self.env.LinkEval(self.policy, self.gamma)
                plotting(self.env.RandNo,self.env.ResDir, Method,EvalDf, MovAvgWin = 15)   
            else:

                self.env.RunNo += 1
                self.env.RandNo += 1

def plotting(RandNo,ResDir, Method,df, MovAvgWin = 15):
    '''Plots ring & Network parameters (density, volume, speed) along with 
    their moving averages. df: containts link results from vissim'''
    #MFD
    XVal = df['AvgK'].values
    YVal = df['AvgQ'].values
    plt.scatter(XVal, YVal,color = 'k',label='Network', alpha = 0.6)
    # plt.legend()
    plt.title('Network Macroscopic Functional Diagram')
    plt.xlabel('Network Average Density (Veh/km)')
    plt.ylabel('Network Average Volume (Veh/hr)')
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
    name = '_'.join([Method,'MFD','RandNo',str(RandNo)])
    name = '.'.join([name,'jpg'])
    PlotFile = os.path.join(ResDir, name)
    plt.savefig(PlotFile)
    plt.close('all')
    
event, values = sg.Window('FileBrowser',[[sg.T('Enter Vissim.inpx file'), 
                                          sg.Input(),sg.FileBrowse(key='-ID1-')],
                                         [sg.T('Select Result Base Folder'), 
                                          sg.Input(),sg.FolderBrowse(key='-ID2-')],
                                         [sg.B('OK'), sg.B('Cancel') ]]).read(close=True)
VFile = os.path.normpath(values['-ID1-']) #File path of vissim.inpx file
Vissim = com.DispatchEx("Vissim.Vissim.800")
BaseDir = os.path.normpath(values['-ID2-'])


                    #----------Input in Vissim--
EpDur,SimRes,RandNo,Repeat,EvalFromTm,EvalInter,CycTm,FFSpd=int(10*3600),3,100,5,0,60,60,60


EvalVar = ['LinkRes','Queues'] #Only link results are required for ring models 
QuickMode=0
VehVisualization =1


InLinks = np.array([1,1,9,16,
                    2,2,21,28,
                    5,5,22,27,
                    6,6,10,15])

ExLinks_st = np.array([2,2,10,20,
                       35,35,22,32,
                       6,6,26,28,
                       34,34,14,16])

ExLinks_TR = np.array([10,20,2,2,
                       22,32,35,35,
                       26,28,6,6,
                       14,16,34,34])

TR= np.array([])
for i in range(0,4):
    TR= np.append(TR,np.array([0.1,0.1,0.2,0.2]))


ST = 0.8*np.ones(len(InLinks))

SC= np.array([])
for i in range(1,5):
    SC= np.append(SC,i*np.ones(4))
SC= np.array(SC, dtype = np.int32)

SG =np.array([])
for i in range(1,5):
    SG= np.append(SG,np.arange(1,5,1))
SG= np.array(SG, dtype = np.int32)


policy = 'P0' #change policy accordingly
gamma = 1 #Change gamma accordingly


Columns = np.array(['SC','SG','InLinks','ExLinks_st','ExLinks_TR',
        'K_InLinks','K_ExLinks_st','K_ExLinks_TR','TR','ST'])
SHdf = pd.DataFrame(columns = Columns)
SHdf['InLinks'] = InLinks
SHdf['ExLinks_st'] = ExLinks_st
SHdf['ExLinks_TR'] = ExLinks_TR
SHdf['TR'] = TR
SHdf['ST'] = ST
SHdf['SC'] = SC
SHdf['SG'] = SG
MFD_df = pd.DataFrame(columns = ['AvgK','AvgQ','AvgS'])
env = VisEnv(Vissim,VFile, SHdf, MFD_df,EpDur,BaseDir,EvalVar,
             SimRes, CycTm,EvalFromTm,EvalInter,FFSpd)
    
Exp = Experiment(env, policy, gamma,BaseDir,
                Repeat, RandNo,
                QuickMode, VehVisualization)
Exp.ExpInitialize()
Exp.RunExp() 