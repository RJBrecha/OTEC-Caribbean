# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 12:24:01 2020

@author: RobertBrecha
"""
#import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MaxNLocator
from mpl_toolkits import mplot3d

from datetime import datetime

headerLine   = 1
nDataRows = 8760

#Read in the Load, Solar and Wind hourly data
fulldf = pd.read_csv(r"C:\Users\Robert Brecha\Documents\Papers\OTEC and SWAC survey\Residual load data.csv')

#Dispatchable renewable power capacity [MW or GW]
DispCap = 2
#Battery storage capacity in MWh or GWh and maximum output power in MW or GW
#BatteryCap = 10
#BatteryMaxPower = min(10,BatteryCap)
#BatteryStart = BatteryCap/2

#set scaling factors such that capacity of both wind and solar are 1MW or 1GW initially; ideally the input data are already scaled so
# these will then be increased through the loops
SolarScale = 1
WindScale = 1
#Extract the load data from the full dataframe; determine the peak load
LoadData = fulldf.Load
PeakLoad = max(LoadData)
#Set the number of hours of battery storage
BatteryHours = 8

#Calculate the residual load for each hour, considering only wind and solar
#Sort the load curve and the residual load curve from highest to lowest
RL1 = fulldf.Load - SolarScale*fulldf.Solar - WindScale*fulldf.Wind
LDC = np.array(LoadData.sort_values(ascending=False))
RLDC1 = np.array(RL1.sort_values(ascending=False))
#plt.plot(LDC)
#plt.plot(RLDC1)

Out = np.empty([1,3])

MaxRLDC = max(LoadData)

#Set the range for scaling factors for scanning the wind and solar pv capacities
X = np.arange(1,10,1)
Y = np.arange(1,10,1)

#Scan through by first setting the wind capacity, then for all solar pv capacities
#in the respective ranges; at each pair (W, S) calculate the residual load, then for 
#different battery capacities, look at the residual load.   When the total residual load
#for all hours is zero, stop and then record the battery capacity.
for W in X:
    for S in Y:
        RL1 = fulldf.Load - S*SolarScale*fulldf.Solar - W*WindScale*fulldf.Wind
        for i in range(1,100,1):
            BatteryCap = i
            B = []
            RL2 = []
            #BatteryMaxPower = min(10,BatteryCap)
            BatteryMaxPower = BatteryCap/BatteryHours
            Batt = BatteryCap/2
#scan through all values of residual load; if greater than zero, you need more
#power.  Either use dispatchable capacity (first choice), or use battery stored
#energy (second choice).  
            for x in RL1:
            #    print('RL_i',x)
                if x > 0:
                    if x > DispCap:
                        x = x - DispCap
            #            print(x)
                        if x <= BatteryMaxPower and x <= Batt:
                            Batt = Batt - x
                            B.append(Batt)
            #                print('Battery=',Batt)
                            x = 0
                        else:
                            x = x - min(BatteryMaxPower, Batt) 
                            Batt = Batt - min(BatteryMaxPower, Batt)
                            B.append(Batt)
            #                print('Battery=',Batt)
                    elif x <= DispCap:
                        Diff = DispCap - x
                        x = 0
                        Batt = Batt + min(Diff,BatteryCap-Batt)
                        B.append(Batt)
            #       RL2.append(x)    
                else:
                    if Batt < BatteryCap:
                        Batt = Batt + min(BatteryMaxPower,-x,BatteryCap-Batt)
                        x = x + min(BatteryMaxPower,-x,BatteryCap-Batt)
                        if Batt < BatteryCap:
                           Batt = Batt + min(DispCap,BatteryCap-Batt)
                    B.append(Batt)
            #    print(Batt)
                RL2.append(x) 
            if max(RL2) <=0.001*max(LoadData):
#                print(BatteryCap)
                Soln = np.array([W,S,BatteryCap]).reshape(1,3)
                break
            BatteryCap = i + BatteryCap
        Soln = np.array([W,S,BatteryCap]).reshape(1,3)
        Out = np.concatenate((Out,Soln),axis = 0)    
    RLDC2 = sorted(np.array(RL2),reverse=True)


    
Out = np.delete(Out,0,0)
#ax = RLDC.plot()
plt.figure(1)
plt.subplot(211)
plt.plot(RLDC1)
plt.plot(RLDC2)

plt.subplot(212)
plt.plot(B)
#ax = RL1.plot()
#ax1 = LoadData.plot()
#ax2 = ResidualLoadData.plot()
Wind = Out[:,0]
Solar = Out[:,1]
Battery = Out[:,2]

#Wind, Solar = np.meshgrid(A,B)

fig = plt.figure()
ax = plt.axes(projection='3d')
surf = ax.plot_trisurf(Wind, Solar, Battery, cmap = cm.jet, linewidth = 0)
fig.colorbar(surf)

ax.set_ylim(10, 0)
#ax.set_zlim(0,4500)
ax.xaxis.set_major_locator(MaxNLocator(5))
ax.yaxis.set_major_locator(MaxNLocator(5))
ax.zaxis.set_major_locator(MaxNLocator(5))
#ax.contour3D(Wind, Solar, Out, 50, cmap='binary')
ax.scatter3D(Wind, Solar, Battery, c=Battery, cmap='Greens');
ax.set_xlabel('Wind capacity [GW]')
ax.set_ylabel('Solar pv capacity [GW]')
ax.set_zlabel('Battery storage [GWh]')

fig.tight_layout()
plt.show()
fig.savefig('DispCap_1a.png')

np.savetxt(r"C:\Users\Robert Brecha\Documents\Energy System Modeling\Australian energy system\DispCap1a.txt",Out)
