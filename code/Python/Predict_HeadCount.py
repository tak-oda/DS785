### This code is Pyomo linear programming equivalent with Optimie_Hiring04.py
### Added headcount dataset and parameterized head count ratio 


from pyomo.environ import *
import numpy as np
import pandas as pd

### PROBLEM DATA ###

### setup ###
file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"
out_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/Prediction"

### PROBLEM DATA ###

# load data
tran1 = pd.read_csv(file_dir + "/pst1.csv")
tran2 = pd.read_csv(file_dir + "/pst2.csv")
tran3 = pd.read_csv(file_dir + "/pst3.csv")
tran4 = pd.read_csv(file_dir + "/pst4.csv")
tran5 = pd.read_csv(file_dir + "/pst5.csv")
tran6 = pd.read_csv(file_dir + "/pst6.csv")
tran7 = pd.read_csv(file_dir + "/pst7.csv")
tran8 = pd.read_csv(file_dir + "/pst8.csv")
tran9 = pd.read_csv(file_dir + "/pst9.csv")
tran10 = pd.read_csv(file_dir + "/pst10.csv")

cycle =  [1,2,3,4,5,6,7,8,9,10] #5 years cycle
stage = [1,2,3,4,5,6,7]
stage_name = ['Associate', 
                   'Consultant', 
                   'Senior Consultant', 
                   'Manager', 
                   'Senior Manager',
                   'Associate Partner',
                   'Partner']

stage_dict = dict( zip(stage, stage_name))
stage_dict['8'] =  'Exit'


#Headcount for each cycle
init_fte = [10,8,6,4,2,1,1]
headcnt_list = [ [5,4,3,2,1,1,1],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0]]

#Revenue per month year by title (unit: K$)
revenue = [20, 24, 30, 40, 50, 60, 80]

tran_list = [tran1,tran2,tran3,tran4,tran5,tran6,tran7,tran8,tran9,tran10 ]



#FTE evolved from itself
fte_from_self = [ 
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0]]


#Calculate evolution of FTE for 5 years

tranList = []
for i in cycle:
    tranList.append (np.round(tran_list[i-1], 3) )
    

for c in cycle:
    
    tran = tranList[c-1]
    for s in stage:
        total_fte = 0
        idx = (c-1)*len(stage) + s -1 #Relative position of hiring parameter
        if c == 1:
            #FTE = tran prob * initial FTE + additional hire
            for s2 in stage:
                total_fte = total_fte + tran.iloc[s2-1,s]*init_fte[s2-1]
                
            total_fte = total_fte 
            fte_from_self[c-1][s-1] = total_fte

        else:
            for s2 in stage:
                total_fte = total_fte + tran.iloc[s2-1,s]*fte_from_self[c-2][s2-1]
                
            total_fte = total_fte 
            fte_from_self[c-1][s-1] = total_fte
                             

np.rev = np.array(revenue)

np.fte0 = np.array(init_fte)

#np.fte1 = np.array(fte_from_self[0])
np.fte10 = np.array(fte_from_self[9])

#np.rev1 = np.sum(np.rev*np.fte1)
np.rev0 = np.sum(np.rev*np.fte0)


np.rev10  = np.sum(np.rev*np.fte10)
#growth = (np.rev10-np.rev1)/np.rev1

growth = (np.rev10-np.rev0)/np.rev0
    

            
np.fte = np.array(fte_from_self[1])
            
            
### OUTPUT ###

#Generate FTE plan

fte_df = pd.DataFrame(columns=[  'cycle', 
                                 'Associate', 
                                 'Consultant', 
                                 'Senior Consultant', 
                                 'Manager',
                                 'Senior Manager',
                                 'Associate Partner',
                                 'Partner'
                                 ],
                      index=range(10))


for c in cycle:
    fte_df.iloc[c-1, 0] =  c
    for s in stage:
       fte_df.iloc[c-1, s]  = fte_from_self[c-1][s-1]

fte_df.to_csv(out_dir + '/fte_plan.csv', index = False)
