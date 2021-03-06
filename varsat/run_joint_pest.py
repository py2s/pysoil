# -*- coding: utf-8 -*-
"""
Created on Sun May 18 12:34:17 2014

@author: redhotkenny
"""

# --------------------------------------------------------------
# --------------------------------------------------------------
# -- Load modules
import numpy as np
import time as time
#from matplotlib import pyplot as plt
from time import *
from math import *
#from matplotlib.backends.backend_pdf import PdfPages
from scipy.sparse.linalg import spsolve
from scipy.sparse.linalg import cg
from scipy.sparse.linalg import cgs
from scipy.sparse import csr_matrix

#load varsat
execfile('varsat_1Da.py')

#  -------------- load Santa CRUZ clim data
# load clim data file
start = time()


####define time period
time0=120*86400  #initial time

T=102*86400     #time period


sup0=(time0)/(15*60)    #define lower limit
sup=(time0+T)/(15*60)+1     #define upper limit


timeobs1=127*86400   #time calibration period starts
T2=95*86400    #length of the calibration period
supobs1=(timeobs1)/(15*60)    #define lower limit for calibration
supobs2=(timeobs1+T2)/(15*60)+1     #define upper limit for calibration


#write limits file, necessary for transpiration estimation with R. 
limitfile=open('period.dat','w')
limitfile.write(str(sup0) + '\n' + str(sup) + '\n')

#Call R to estimate Transpiration
    # I cannot run R from here, so R is execute directly on the executable file. If limits are changed
        #this program should be run twice in order to work propertly
#import subprocess
#subprocess.call('R CMD BATCH ETP_cal.R',shell=True)

##Interception Model
    #   Either run the interception model (1) or use the output of the interception model (2)



####(1)


#load data for interception model
import csv
csvfile= open('clim_data300.csv', "rU")
csv_file = csv.reader(csvfile, delimiter=',')
# eliminate blank rows if they exist
rows = [row for row in csv_file if row]
taille = len(rows)
headings = rows[0] # get headings


Rain_clim=np.zeros(sup-sup0)

rows=np.array(rows)
for i in range(int(sup0+1),int(sup+1)):
    Rain_clim[i-sup0-1]=float(rows[i][5])



###load transpiration data from R output

import csv
tranfile = open('transp.csv', "rU")
tran_file = csv.reader(tranfile, delimiter=',')
# eliminate blank rows if they exist
rows = [row for row in tran_file if row]
taille = len(rows)
headings = rows[0] # get headings

ETP=np.zeros(sup-sup0)
rows=np.array(rows)
for i in range(1,len(ETP)+1):
   ETP[i-1]=float(rows[i][0]) 



##Data as fluxes for soil model
TF=Rain_clim/(1000*15*60)
ETP=ETP/(1000*15*60)


# Soil characteristics 
paramfile= open('param.dat', 'r')
Rs_p = float(paramfile.readline())
Ksat1 = float(paramfile.readline()) 
theta_r1 = float(paramfile.readline())
theta_s1 = float(paramfile.readline())
n1 = float(paramfile.readline())
alpha1 = float(paramfile.readline())
Ksat2 = float(paramfile.readline()) 
theta_r2 = float(paramfile.readline())
theta_s2 = float(paramfile.readline())
n2 = float(paramfile.readline())
alpha2 = float(paramfile.readline())
Ksat3 = float(paramfile.readline()) 
theta_r3 = float(paramfile.readline())
theta_s3 = float(paramfile.readline())
n3 = float(paramfile.readline())
alpha3 = float(paramfile.readline())
Ksat4 = float(paramfile.readline()) 
theta_r4 = float(paramfile.readline())
theta_s4 = float(paramfile.readline())
n4 = float(paramfile.readline())
alpha4 = float(paramfile.readline())


numlay=4 #number of layers
LC=np.array([0.3,0.8,2.1])  #deep of first layer
L = 2.2 # model length [m]
#dt = 60 # time step [s]
dz = 0.02 # mesh cell size [m]
I = int(round(L/dz)+1) # number of nodes
z = np.linspace(0,L,I)
hFC=-1.02   #head pressure at field capacity
pp=100. #this value is not take into account

FC11= theta_r1 + (theta_s1 - theta_r1) * (1 + abs(alpha1*hFC)**n1)**(-(1.-1./n1)) #field capacity
FC12= theta_r2 + (theta_s2 - theta_r2) * (1 + abs(alpha2*hFC)**n2)**(-(1.-1./n2)) #field capacity


soil_data = {'Ksat':[Ksat1,Ksat2,Ksat3,Ksat4], 'Ss':[0.,0.,0.,0.], 'eta':[theta_s1,theta_s2,theta_s2,theta_s2], 'theta_r' : [theta_r1,theta_r2,theta_r2,theta_r2], 'theta_s' : [theta_s1,theta_s2,theta_s2,theta_s2], 'n':[n1,n2,n2,n2], 'alpha':[alpha1,alpha2,alpha2,alpha2], 'FC1':[FC11, FC12,FC12,FC12], 'FC2':[theta_s1,theta_s2,theta_s2,theta_s2]}

soil_carac = get_soil_carac(numlay,L,dz,LC,soil_data,z,pp)

# time and space discretization
timestep=np.linspace(0.,(sup-1)*15*60,sup)


tstep=100.

#Root Information
LR=0.6
type='homogeneous'
#get Root Distribution

RD = get_RD(L, I, LR, z, dz, type) 


# boundary conditions
h_top = -TF
bc = {'time':timestep,'top':['fixed_flow',h_top],'bot':['free_drainage']}

# source term
q = ETP
#q=np.zeros(sup)
        
h_init = np.array([-0.25]*I)



# --------------------- Simulation run --------------------------

S = run_varsat(L, T, dz, tstep, h_init, bc, q, soil_carac)


#import csv
#soilfile=open('300M_SoilDATA.csv', "rU")
#soil_file = csv.reader(soilfile, delimiter=',')
# eliminate blank rows if they exist
#rows = [row for row in soil_file if row]
#taille = len(rows)
#headings = rows[0] # get headings



####OJO!!!!
prof1=0.56
prof2=0.40
prof3=0.26
ob1=int((L-prof1)/dz)
ob2=int((L-prof2)/dz)
ob3=int((L-prof3)/dz)


outputfile=open('output.dat', 'w')
for i in range(0,int(supobs2-sup0)):
    outputfile.write( str(round(S[ob1,i],5)) + '\n' + str(round(S[ob2,i],5)) + '\n' + str(round(S[ob3,i],5)) + '\n')
#for i in range(supobs1,supobs2):
#    if float(rows[i+sup0+1][14])<0:
#        outputfile.write( str(round(S[ob3,i],5)) + '\n')
#for i in range(supobs1,supobs2):
#    if float(rows[i+sup0+1][18])<0:
#        outputfile.write( str(round(S[ob4,i],5)) + '\n')



elapsed = (time() - start)
print(elapsed)



