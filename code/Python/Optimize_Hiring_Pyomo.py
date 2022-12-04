### This code is Pyomo linear programming equivalent with Optimie_Hiring04.py
### Added headcount dataset and parameterized head count ratio 


from pyomo.environ import *
import numpy as np
import pandas as pd

### PROBLEM DATA ###

### setup ###
file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"
out_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/linear_programming"

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


#Maximum number of hiring for each position per cycle
bond_hire = [ (0,10),
             (0,10),
             (0,10),
             (0,5),
             (0,2),
             (0,1),
             (0,1)
             ]

#Minimum head count ratio (Span of control)
ratio_ast_mng = 2
ratio_con_mng = 2
ratio_sc_mng = 1
ratio_mng_sm = 2
ratio_mng_pt = 2.5
ratio_sm_pt = 2
ratio_sm_ap = 2

### MODEL CONSTRUCTION ###
#Declaration
model = ConcreteModel()

#Decision Variables
model.x = Var(range(70), domain=NonNegativeReals)


cycle =  [1,2,3,4,5,6,7,8,9,10] #5 years cycle
#cycle = [1,2,3]
stage = [1,2,3,4,5,6,7]
#stage = [1,2]

revenue = [20, 24, 30, 40, 50, 60, 80]
   

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
                
            total_fte = total_fte + model.x[idx]    
            fte_from_self[c-1][s-1] = total_fte

        else:
            for s2 in stage:
                total_fte = total_fte + tran.iloc[s2-1,s]*fte_from_self[c-2][s2-1]
                
            total_fte = total_fte + model.x[idx]  
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
            
            

#Objective
#model.profit = Objective(expr=sum(np.fte),
#                     sense=maximize)

model.growth = Objective(expr=growth,
                     sense=maximize)


#model.growth.pprint()


model.fte_ratio = ConstraintList()

#Constraint
for c in cycle:
    
    ast_fte = fte_from_self[c-1][0]
    con_fte = fte_from_self[c-1][1]
    sc_fte = fte_from_self[c-1][2]
    mng_fte = fte_from_self[c-1][3]
    sm_fte = fte_from_self[c-1][4]
    ap_fte = fte_from_self[c-1][5]
    pt_fte = fte_from_self[c-1][6]   
    

    model.fte_ratio.add( expr = ast_fte -1*ratio_ast_mng*mng_fte  >= 0 )
    model.fte_ratio.add( expr = con_fte -1*ratio_con_mng*mng_fte  >= 0 )
    model.fte_ratio.add( expr = sc_fte  -1*ratio_sc_mng*mng_fte  >= 0 )
    model.fte_ratio.add( expr = mng_fte -1*ratio_mng_sm* sm_fte  >= 0 )
    model.fte_ratio.add( expr = mng_fte -1*ratio_mng_pt* pt_fte  >= 0 )
    model.fte_ratio.add( expr = sm_fte  -1*ratio_sm_pt*pt_fte  >= 0 )
    model.fte_ratio.add( expr = sm_fte  -1*ratio_sm_ap*ap_fte  >= 0 )

#Boundary
for c in cycle:
    for s in stage:
        idx = (c-1)*len(stage) + s -1 #Relative position of hiring parameter
        
        lower = 0
        upper =  bond_hire[s-1][1]
        
        model.fte_ratio.add (expr = model.x[idx] <= upper)
       
    
    
#model.fte_ratio.pprint()
    
solver = SolverFactory('glpk')
solver.solve(model)

### OUTPUT ###

# note that we're using f-strings for output here which is a little different and cleaner than in the video
print(f"Maximum Growth = {100*model.growth():,.2f}%")

hiring = np.zeros(70)

for i in range(70):
    hiring[i] = np.round(model.x[i]())
hiring_mtx = np.reshape(hiring, (10,7))
hiring_df = pd.DataFrame(hiring_mtx, columns=stage_name)

hiring_df.to_csv(out_dir + '/hiring_plan_pyomo.csv', index = True)


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
       fte_df.iloc[c-1, s]  = fte_from_self[c-1][s-1]()

fte_df.to_csv(out_dir + '/fte_plan_pyomo.csv', index = False)
