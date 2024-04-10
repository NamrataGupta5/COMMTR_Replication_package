# -*- coding: utf-8 -*-
"""
Created on Sat Sep 13 11:52:23 2021

Input: 1) Vissim files and directory
       2) Basic simulation parameters
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
            Ring1, Ring2, Ring3 --> Array of links forming each ring
            TurnRatio --> Array of turn ratios


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
import warnings
import PySimpleGUI as sg
import re
import win32com.client as com
import os, shutil
import matplotlib.pyplot as plt
from datetime import datetime


warnings.simplefilter(action='ignore', category=FutureWarning)

####------------User Inputs------------

                    #---Vissim file and directory
event, values = sg.Window('FileBrowser',[[sg.T('Enter Vissim.inpx file'), 
                                          sg.Input(),sg.FileBrowse(key='-ID1-')],
                                         [sg.T('Select Result Base Folder'), 
                                          sg.Input(),sg.FolderBrowse(key='-ID2-')],
                                         [sg.B('OK'), sg.B('Cancel') ]]).read(close=True) # Takes input of vissim file and base folder directory
VFile = os.path.normpath(values['-ID1-']) #File path of vissim.inpx file
Vissim = com.DispatchEx("Vissim.Vissim.600")
BaseDir = os.path.normpath(values['-ID2-'])

#------
time_start = datetime.now()
                    #----------Input in Vissim--
EpDur,SimRes,RandNo,Repeat,EvalFromTm,EvalInter,CycTm=15*3600,3,42,40,0,60,60
DesEvalInt = 60    #Eval Interval for final analysis
LoadInt = 0 #No new vehicle is enter after this
EvalVar = ['LinkRes','Queues'] #Only link results are required for ring models 

                    #------Vissim Network inputs

Ring3 = np.array([1,2,6,7,16,10000,10001,10002,10003,10019]) # Array of links that form a Ring3
Ring2 = np.array([3,4,5,8,13,10004,10005,10006,10007,10016]) # Array of links that form a Ring2
Ring1 = np.array([9,10,11,12,15,10008,10009,10010,10011,10018]) # Array of links that form a Ring1

Rings = np.array([Ring1,Ring2,Ring3])
FFSpd = 60
JamSpd  = 3
PhNum = 4 # User decides
TurnRatio = [0.1,0.1,0.2,0.2]  #User input Turn ratio from one ring to another in each phase

InOutPair = [[1,2],[1,3],[2,1],[3,1]] #User input pair {1,2} shows link b/w ring 1->2

                 #----------Experiment inputs----
Gamma = [0, 0.3, 1]
Policy = ['P0','P1']
Network = 'E'

Dir2 = BaseDir
#------------------Inputs Processing-------------
            #----Preparing Controller database
SigContDB = pd.DataFrame(columns=['PhNum','SGs','InOutPair',
                                  'TurnRatio','Pressure',
                                  'TurnDensity','GrTm'],
                         index = np.arange(1, PhNum +1, 1)) #controller database
SigContDB['PhNum']=np.arange(1, PhNum +1, 1)
SigContDB['SGs']=np.arange(1, PhNum +1, 1)#From Vissim (informs signalgrps # of a phase)
SigContDB['TurnRatio'] = TurnRatio
SigContDB['InOutPair'] = InOutPair
SigContDB['Pressure'] = np.zeros(PhNum) #Stores phase-wise pressure
SigContDB['TurnDensity'] = np.zeros(PhNum) #Expected turn density of a ring e.g. TR*RingDensity
SigContDB['GrTm'] = np.zeros(PhNum) #Stores phase-wise green time
SigContDB = SigContDB.set_index('PhNum') #setting phase number as index
            #-------Preparing experiments database
Col_Arr = ['Policy', 'Gamma','CycTm', 'Network', 'RunNo','RandNo','GridlockTime',
           'AvgK','R1_K','R2_K','R3_K']
ExpDataBase = pd.DataFrame(columns=Col_Arr)
DBName = "".join(['GridLockDB','.att'])
DBPath = os.path.join(Dir2,DBName)
while os.path.exists(DBPath): #ensuring that DirPath doesn't pre-exist 
    DBName = '_'.join([DBName,str(1)])
    DBPath = os.path.join(Dir2, DBName)
ExpDataBase.to_csv(DBPath, sep=';',index = False)

def plotting(RandNo,ResDir,Rings, Method,df, MovAvgWin = 15):
    '''Plots ring & Network parameters (density, volume, speed) along with 
    their moving averages. df: containts link results from vissim'''
    x = np.arange(1,df.shape[0]+1)
    colors = ['r','g','b']
    Vars = [['Density','(Veh/km)','K'],
            ['Volume','(Veh/hr)','Q'],
            ['Speed','(Km/hr)','S']]
    RingVar =[]
    for i in range(len(Rings)):
        RingVar.append(['Ring{}'.format(i+1),'R{}_'.format(i+1)])
    RingVar.append(['Network Average','Avg'])
    for Vs in Vars:
        plt.close('all')
        ylim = [0,0]
        xlim = [np.nanmin(x),np.nanmax(x)]
        xint = int((xlim[1]-xlim[0])/10)
        temp = (xlim[1]+xint)%10
        temp = 10-temp
        xlim[1] =xlim[1]+ temp
        temp = np.array([xint%10,xint%5])
        temp = np.array([10,5])-temp
        xint =xint+ np.min(temp)
        # fig = plt.figure()
        ax = plt.axes()
        for (r,c) in zip(RingVar,colors):
            Para = ''.join([r[-1],Vs[-1]])
            Para_MA = df[Para].rolling(MovAvgWin).mean().values
            Para = df[Para].values
            # ylim[0] = min([ylim[0],np.nanmin(Para),np.nanmin(Para_MA)])
            ylim[1] = max([ylim[1],np.nanmax(Para),np.nanmax(Para_MA)])
            plt.plot(x, Para,'-',color = c,
                     label=r[0],linewidth = 1,alpha = 0.5)
            label = "{}: Moving average".format(r[0])
            plt.plot(x, Para_MA,'--',color = c, 
                     label=label,linewidth = 2)
        temp = ylim[1]%10
        temp = 10-temp
        ylim[1] =ylim[1]+ temp
        yint = int((ylim[1]-ylim[0])/10)
        temp = np.array([yint%10,yint%5])
        temp = np.array([10,5])-temp
        yint =yint+ np.min(temp)
        plt.xlim(xmin=xlim[0], xmax=xlim[1])
        plt.ylim(ymin=ylim[0], ymax=ylim[1]+yint)
        plt.xticks(np.arange(xlim[0], xlim[1], xint))
        plt.yticks(np.arange(ylim[0], ylim[1]+yint, yint))
        plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
        # plt.legend()
        box = ax.get_position()
        ax.set_position([box.x0, box.y0+ box.height*0.2, box.width, box.height*0.85])
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                   fancybox=True, shadow=True, ncol=3,fontsize='x-small')
        plt.title("{} Variation".format(Vs[0]))
        plt.xlabel('Timestep') 
        plt.ylabel("{} {}".format(Vs[0],Vs[1]))
        # plt.legend(loc='lower right')
        name = '_'.join([Method,Vs[0],'RandNo',str(RandNo)])
        name = '.'.join([name,'jpg'])
        PlotFile = os.path.join(ResDir, name)
        plt.savefig(PlotFile)
    plt.close('all')
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



def InVisSet(Vissim,Sim,Eval,ResDir,EvalVar,EpDur=10400, SimRes=3,
             EvalFromTm = 0,EvalInter=60,CycTm=60):
    '''Sets initial values in vissim'''
    Sim.SetAttValue('SimPeriod',EpDur+1) #episode duration
    Sim.SetAttValue('SimRes',SimRes) #sim resolution
    Eval.SetAttValue('EvalOutDir',ResDir)
    Parameter = ['CollectData','FromTime','ToTime','Interval'] #eval conf
    ParValues = [1,EvalFromTm,EpDur,EvalInter]
    for V in EvalVar:
        count = 0
        for P in Parameter:
            PV = ParValues[count]
            Eval.SetAttValue(''.join([V,P]),PV)
            Vissim.Evaluation.SetAttValue(''.join([V,P]),PV)
            count +=1

def GreenTm(Density, Policy,SigContDB, CycTm, Gamma):
    '''Calculate green time for BP and adaptive signal controllers'''
    PhNum = SigContDB.shape[0]
    MinGr = ((1-Gamma)*CycTm/PhNum)
    GrTm = (CycTm/PhNum)*np.ones(PhNum)
    for iterator in SigContDB.itertuples():
        index = iterator.Index
        InOut = iterator.InOutPair
        TR = iterator.TurnRatio
        if 'P1' in Policy:
            Xin = Density[int(InOut[0])-1]
            Xout = Density[int(InOut[1])-1]
            Press = max(0,round((Xin-Xout),2))
            SigContDB.at[index,'Pressure'] = Press
            Para = 'Pressure'
        else:
            SigContDB.at[index,'TurnDensity'] = TR*Density[InOut[0]-1] 
            SigContDB.at[index,'TurnDensity'] = Density[InOut[0]-1] 
            Para = 'TurnDensity'
    Tot =  SigContDB[Para].sum()
    if (Tot):
        GrTm = (SigContDB[Para].values)*Gamma*CycTm/Tot +MinGr*np.ones(PhNum)   
    IntArr = np.array(GrTm, dtype = np.dtype('int8'))
    diff =np.sum(GrTm) - np.sum(IntArr)
    ID = np.random.choice(np.where(IntArr == np.min(IntArr))[0]) # selects random index of phase with smallest green time
    IntArr[ID] += diff # Add the difference to randomly selected phase
    SigContDB['GrTm'] = IntArr
    return SigContDB


def Density(Vissim, Net,Rings):
    '''Obtains ring density from vissim before each cycle'''
    LinkObj = Net.Links
    RelAtt = ['No','NumLanes','Length2D',
              'Avg:LinkEvalSegs\Density(Current,Last,All)'] # The command gives avg density of the link (avg in interval & avg in lanes)
                                                            # Works when vissim collects per lane data
    values = LinkObj.GetMultipleAttributes(RelAtt)
    col = ['Link','Lanes','Length','Density']
    df = pd.DataFrame(values,columns= col, dtype = np.float32)
    df.fillna(0,inplace = True)
    df['Length'] = df['Length'].mul(df['Lanes'], axis = 'index') # ni*li
    df['KmulL'] = df['Density'].mul(df['Length'], axis = 'index') # (Avg ki (veh/hr/lane))*ni*li
    RingDensity = []
    for r in Rings:
        RD = np.round(df[df['Link'].isin(r)]['KmulL'].sum()/\
                      df[df['Link'].isin(r)]['Length'].sum(),2)  # Avg veh/hr/lane density of ring r
        RingDensity.append(RD)
    return np.array(RingDensity)


def AvgSpeed(Vissim,Net, Rings, FFSpd=60):
    '''Obtains Network's average speed for gridlock comparison'''
    LinkObj = Net.Links
    RelAtt = ['No','NumLanes','Length2D',
              'Avg:LinkEvalSegs\Speed(Current,Last,All)'] # The command gives avg speed of the link (avg in interval & avg in lanes)
                                                            # Works when vissim collects per lane data
    values = LinkObj.GetMultipleAttributes(RelAtt)
    col = ['Link','Lanes','Length','Speed']
    df = pd.DataFrame(values,columns= col, dtype = np.float32)
    df.fillna(0,inplace = True)
    df = df.replace([''],str(FFSpd)) #'' comes when there is no vehicle on the link; essentially link is in free-flow
    temp = df['Speed']
    for i in range(len(temp)):
        if temp[i] == '':
            temp[i] = 0
        else:
            temp[i] = float(temp[i])
    df['Speed'] = temp
    df['Length'] = df['Length'].mul(df['Lanes'], axis = 'index')  # ni*li
    df['SmulL'] = df['Speed'].mul(df['Length'], axis = 'index') # (Avg vi (veh/hr/lane))*ni*li
    SmulL = df['SmulL'].sum()
    r = np.reshape(Rings, -1)
    AvgSpd = np.round(SmulL/df[df['Link'].isin(r)]['Length'].sum(),2) #Avg network speed
    return AvgSpd

def RingEval(Vissim,Net,Rings,EpDur,EvalFromTm, EvalInter, RunNo,  FFSpd=60):
    '''Calculate ring and network parameter after each Run. For average 
    of an experiment RunNo = "Avg"'''
    LinkObj = Net.Links # link objects
    NumofInt = int((EpDur -EvalFromTm)/EvalInter) # Number of intervals 
    col = ['Interval','Avg:LinkEvalSegs\Density', 'Avg:LinkEvalSegs\Speed', 
           'Avg:LinkEvalSegs\Volume','NumLanes', 'Length2D','No'] #'Avg:LinkEvalSegs\ gives avg link parameter (avg in interval & avg in lanes)
                                                            # Works when vissim collects per lane data
    dfcol = [re.findall(r"[\w']+", col[i])[-1] \
                    for i in range(0,len(col),1)] #data frame column names
    EvalDfCol = []
    VarSymb = ['K','Q','S']
    for i in range(len(Rings)):
        for v in VarSymb:
            EvalDfCol.append("R{}_{}".format((i+1),v))
    EvalDf = pd.DataFrame(columns = EvalDfCol,
                          index = np.arange(1, NumofInt +1, 1)) #initialized evaluation df
    index = 0 
    for i in range(NumofInt):
        index = i+1
        st_tm = EvalFromTm + (i)*EvalInter #start time of interval i
        ed_tm = st_tm + EvalInter #end time of interval i
        RelAtt = [] # parameters requiring extraction from vissim
        for j in range(1,len(col),1):
            if col[j] == 'Length2D' or col[j] == 'No'or col[j] == 'NumLanes':
                RelAtt.append(col[j])
            else:
                att = ''.join([col[j],"(",str(RunNo),',',str(index),",all)"])
                RelAtt.append(att)
        values = LinkObj.GetMultipleAttributes(RelAtt) #values extracted from vissim
        df = pd.DataFrame(values,columns= dfcol[1:], dtype = np.float32) #data frame from values
        df.fillna(0,inplace = True) # removing Nan
        df = df.replace([''],str(FFSpd)) #'' comes only for speed column when there is no vehicle on the link;
                                            #essentially link is in free-flow
        df['Length2D'] = df['Length2D'].mul(df['NumLanes'], axis = 'index') # ni*li
        VarName = ['Density','Volume','Speed']
        VarAvgVal = [0,0,0]
        DictSymb = dict(zip(VarSymb,VarName))
        DictAvgVal = dict(zip(VarSymb,VarAvgVal))
        L = [df[df['No'].isin(Rings[i])]['Length2D'].sum() for i in range(len(Rings))] #[n1*length_ring1,n2*length_ring2,n3*length_ring3]
        # count = 0
        for c in EvalDfCol:
            VS = c[-1] #e.g. 'K'
            VN = DictSymb[VS] #e.g. VN = 'Density'
            RingNo = int(re.search(r'\d+', c).group())-1 #e.g. RingNo=0
            R = Rings[RingNo] #array of links in a ring
            VSmulL = '{}mulL'.format(VS) #e.g. 'KmulL'
            df[VSmulL] = df[VN].mul(df['Length2D'], axis = 'index') #Variable*D
            EvalDf.at[index,c] = np.round(df[df['No'].isin(R)][VSmulL].sum()/ L[RingNo],0) #Avg ring parameter
            DictAvgVal[VS] += df[df['No'].isin(R)][VSmulL].sum() 
            # count+=1
        AvgCol = ['Avg{}'.format(i) for i in VarSymb]
        AvgVal = np.round(np.array(list(DictAvgVal.values()))/sum(L),0)
        EvalDf.at[index,AvgCol] = AvgVal
        EvalDf.at[index,'Interval'] = '_'.join([str(st_tm),str(ed_tm)]) #interval e.g. 0_60
        EvalDf.at[index,'FromTm'] = st_tm #start time e.g. 0
        EvalDf.at[index,'ToTm'] = ed_tm   #end time  e.g. 60
    return EvalDf,EvalDfCol

def DataProMod(Vissim, Net,Rings,Policy,Gamma,ResDir,BaseDir,
            EpDur, EvalFromTm, EvalInter,ExpDataBase, RandNo,RunNo, DesEvalInt):
    '''Updates experiment database'''
    Method = "_".join([Policy, 'G',str(Gamma)]) #Converting vehicle input to string
    FlName = '_'.join([Method,str(RandNo)])  #e.g. BP_35_35
    EvalDf,EvalDfCol = RingEval(Vissim,Net,Rings,EpDur,EvalFromTm, EvalInter, RunNo) #Link evaluation results
    AccumFrame = int(DesEvalInt/EvalInter)
    ChCol = np.array(['Interval', 'FromTm', 'ToTm'])
    for c in EvalDf.columns:
        if not np.any(ChCol == c):
            EvalDf[c] = EvalDf[c].rolling(AccumFrame).mean().values
    ToTm_Val = np.array([60*(i+1) for i in range(EvalDf.shape[0])])
    EvalDf = EvalDf[EvalDf['ToTm'].isin(ToTm_Val)]
    
    AggResultFl = os.path.join(ResDir,''.join([FlName,'.att'])) #path of result file
    EvalDf.to_csv(AggResultFl, sep=';',index = False) #storing csv file
    plotting(RandNo,ResDir,Rings, Method,EvalDf, MovAvgWin = 15)
    if RunNo == 'Avg':
        AutoResDir = '.'.join([Vissim.AttValue('InputFile').split('.')[0],
                               'results']) #automatically generated result directory
        ResDirPath = os.path.join(BaseDir, AutoResDir) #Result dir path
        shutil.rmtree(ResDirPath) #deleting automatically generated results to start fresh for next experiment
    ind = ExpDataBase.shape[0]-1
    temp = EvalDf[EvalDf['AvgK']!=0].tail(15).mean()
    ExpDataBase.at[ind,'R1_K'] =np.round(temp['R1_K'],0)
    ExpDataBase.at[ind,'R2_K'] =np.round(temp['R2_K'],0)
    ExpDataBase.at[ind,'R3_K'] =np.round(temp['R3_K'],0)
    ExpDataBase.at[ind,'AvgK'] =np.round(temp['AvgK'],0)
    return ExpDataBase

def RunCycle(Vissim,Sim,Net,SC, GrTm,EpCount,SimRes,EpDur):
    '''Runs cycle in vissim'''
    GCount = GrTm[0]
    CycCount = sum(GrTm)
    if EpCount == EpDur:
        for i in range(SimRes):
            Sim.RunSingleStep()
        GCount -=1
        CycCount-=1
        EpCount-=1
    SigGrps = SigContDB['SGs'].values #Needs to be modified for phases e multi Sig Grps
    SigStat = ['RED' for i in range(len(SigGrps))]
    ActPh = 0
    SigStat[0] = 'GREEN'
    SigDict = dict(zip(SigGrps,SigStat)) 
    SC.SGs.SetMultiAttValues('State',tuple(SigDict.items()))  
    while (CycCount):
        if EpCount == 0:
            break
        while (GCount):
            if EpCount == 0:
                break
            else:
                for i in range(SimRes):
                    Sim.RunSingleStep()
                GCount -=1
                CycCount -=1
                EpCount -=1
        SigStat[ActPh]='RED'
        ActPh += 1
        if ActPh < len(GrTm):
            GCount = GrTm[ActPh]
            SigStat[ActPh]='GREEN'
            SigDict = dict(zip(SigGrps,SigStat)) 
            SC.SGs.SetMultiAttValues('State',tuple(SigDict.items()))   
    return EpCount

def RunExp(Vissim,VFile,EvalVar,LoadInt,ExpDataBase,SigContDB,Dir2,
           Rings,Policy,Network,BaseDir,DBPath,JamSpd,RandNo = 42,Repeat =5,CycTm =60,EpDur=10400, 
           SimRes=3,EvalFromTm = 0, EvalInter=60,Gamma =0,DesEvalInt=60):
    # VehInpStr = "_".join(map(str, VehInp))
    DirName = Policy
    ResDir = os.path.join(Dir2, Policy) #to store results of current exp
    while os.path.exists(ResDir): #ensuring that DirPath doesn't pre-exist 
        DirName = '_'.join([DirName,str(1)])
        ResDir = os.path.join(Dir2, DirName)
    os.mkdir(ResDir) #Creating new directory (eg: NormQ_200_1...)to store results of current exp
    # RandNo = 42
    PhNum = SigContDB.shape[0]
    SigGrps = SigContDB['SGs'].values #Needs to be modified for phases e multi Sig Grps
    Vissim.LoadNet(VFile)
    Net = Vissim.Net
    Sim = Vissim.Simulation
    Graph = Vissim.Graphics.CurrentNetworkWindow
    Eval = Vissim.Evaluation
    InVisSet(Vissim,Sim,Eval,ResDir,EvalVar,EpDur=EpDur, SimRes=SimRes,
             EvalFromTm = EvalFromTm,EvalInter=EvalInter,CycTm =CycTm)
    #Check vissim model for Ring1_TR, Ring2_TR, and Ring3_TR
    Ring1_TR = {1:0,2:0,3:1} # 1&2 corresponds to turning movement; 3 is within the ring
    Ring2_TR = {1:0,2:1}     # 1 corresponds to turning movement; 2 is within the ring
    Ring3_TR = {1:0,2:1}     # 1 corresponds to turning movement; 2 is within the ring
    RingTR = [Ring1_TR,Ring2_TR,Ring3_TR]
    TR_Values = SigContDB.TurnRatio.values
    for r in range(Repeat):
        ind = ExpDataBase.shape[0]
        col = ['Policy', 'Gamma','CycTm', 'Network', 'RunNo','RandNo']
        val = [Policy,Gamma, CycTm, Network, r+1,RandNo]
        ExpDataBase.at[ind,col] = val
        Sim.SetAttValue('RandSeed', RandNo) #Random seed change in vissim       
        EpCount = EpDur #episode count down counter
        Flag = 0 
        FlagTot = 0
        JamTime = EpDur
        ExpDataBase.at[ind,'GridlockTime'] = JamTime
        TR_Object =  Net.VehicleRoutingDecisionsStatic.GetAll
        Route_Ring_TR = [t.VehRoutSta for t in TR_Object]
        Graph.SetAttValue("QuickMode",1)
        Graph.SetAttValue("VehVisualization",0)
        while(EpCount):
            if EpCount == EpDur:
                temp =0 
                for TR in Route_Ring_TR:
                    TR.SetMultiAttValues('RelFlow(1)',tuple(RingTR[temp].items()))
                    temp +=1
                for i in range(SimRes):
                    Sim.RunSingleStep()
                EpCount-=1
                SigStat = ['GREEN' for i in range(len(SigGrps))]
                SC = Net.SignalControllers.ItemByKey(1) #Vissim object
                SigDict = dict(zip(SigGrps,SigStat)) 
                SC.SGs.SetMultiAttValues('State',tuple(SigDict.items())) 
                while(Sim.AttValue('SimSec')<LoadInt):
                    Sim.RunSingleStep()
                EpCount-=LoadInt
            Ring1_TR1 = {1:TR_Values[0], 2:TR_Values[1], 3:1-TR_Values[0]-TR_Values[1]} # 1&2 corresponds to turning movement; 3 is within the ring
            Ring2_TR1 = {1:TR_Values[2], 2:1-TR_Values[2]}     # 1 corresponds to turning movement; 2 is within the ring
            Ring3_TR1 = {1:TR_Values[3], 2:1-TR_Values[3]}     # 1 corresponds to turning movement; 2 is within the ring
            RingTR1 = [Ring1_TR1,Ring2_TR1,Ring3_TR1]
            temp =0 
            for TR in Route_Ring_TR:
                TR.SetMultiAttValues('RelFlow(1)',tuple(RingTR1[temp].items()))
                temp +=1
            Arr= Density(Vissim, Net,Rings)
            AvgSpd = AvgSpeed(Vissim,Net, Rings)
            if AvgSpd < JamSpd and sum(Arr) > 10:
                Flag = 1
            else:
                Flag = 0
            if (Flag):
                FlagTot += Flag
            else:
                FlagTot = 0
            if FlagTot >= 15:
                JamTime = np.round(Sim.AttValue('SimSec') - 15*60,0)
                ExpDataBase.at[ind,'GridlockTime'] = JamTime
                break
            SigContDB = GreenTm(Arr, Policy,SigContDB, CycTm, Gamma)
            GrTm = SigContDB['GrTm'].values
            EpCount = RunCycle(Vissim,Sim,Net,SC, GrTm,EpCount,SimRes,EpDur)
        Sim.Stop()
        RunNo = r+1
        ExpDataBase = DataProMod(Vissim, Net,Rings,Policy,Gamma,ResDir,BaseDir,
                                 EpDur, EvalFromTm, EvalInter,ExpDataBase, 
                                 RandNo,RunNo, DesEvalInt)
        ExpDataBase.to_csv(DBPath, sep=';',index = False)
        RandNo +=1 #increasing Random seed for next episode
    RunNo = 'Avg'
    RandNo = 'Avg'
    ind = ExpDataBase.shape[0]
    col = ['Policy', 'Gamma','CycTm', 'Network', 'RunNo','RandNo','GridlockTime']
    val = [Policy,Gamma, CycTm, Network,'Avg','Avg','Avg']
    ExpDataBase.at[ind,col] = val
    ExpDataBase =DataProMod(Vissim, Net,Rings,Policy,Gamma,ResDir,BaseDir,
                                 EpDur, EvalFromTm, EvalInter,ExpDataBase, 
                                 RandNo,RunNo, DesEvalInt)
    ExpDataBase.to_csv(DBPath, sep=';',index = False)
    return ExpDataBase

def main(ExpDataBase):
    for p in Policy:
        i = 0
        for g in Gamma:
            if (p=='P1' and not g in [0]) or (p == 'P0'):
                ExpDataBase = RunExp(Vissim,VFile,EvalVar,LoadInt,ExpDataBase,
                              SigContDB,Dir2,Rings,p,Network,BaseDir,DBPath,
                              JamSpd,RandNo,Repeat,CycTm,EpDur, SimRes,EvalFromTm,
                              EvalInter , g,DesEvalInt)
            i+=1
    time_end = datetime.now()
    print(f'Total time = {(time_end - time_start).seconds} seconds')
        
if __name__ == '__main__':
      main(ExpDataBase)

