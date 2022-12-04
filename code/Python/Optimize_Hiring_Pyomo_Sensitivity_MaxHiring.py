### This code is to perform sensitivity analysis around different parameter of maximum number of hiring




from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition

import numpy as np
import pandas as pd
import copy
import itertools

### PROBLEM DATA ###

### setup ###
file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"
out_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/linear_programming"

### PROBLEM DATA ###

# load data
# Transition matrix
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
init_fte = [5,4,3,2,1,1,1]
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





#Optimize hiring 
#Var: ratio_list: List of head count ration set
#Var: bond_hire: List of allowable range of hiring per cycle
#Var: tran_list: Transition matrix
#Return: Growth rate and total number of hiring from position A to P
def optimize_hiring(ratio_list, bond_hire, tran_list):

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
    
    ratio_ast_mng = ratio_list[0]
    ratio_con_mng = ratio_list[1]
    ratio_mng_sm = ratio_list[2]
    ratio_mng_pt = ratio_list[3]
    ratio_sm_pt = ratio_list[4]
    ratio_sm_ap = ratio_list[5]
    
    for c in cycle:
        
        ast_fte = fte_from_self[c-1][0]
        con_fte = fte_from_self[c-1][1]
        mng_fte = fte_from_self[c-1][3]
        sm_fte = fte_from_self[c-1][4]
        ap_fte = fte_from_self[c-1][5]
        pt_fte = fte_from_self[c-1][6]   
        
        model.fte_ratio.add( expr = ast_fte -1*ratio_ast_mng*mng_fte  >= 0 )
        model.fte_ratio.add( expr = con_fte -1*ratio_con_mng*mng_fte  >= 0 )
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
           
        
        
        
        
    solver = SolverFactory('glpk')
    result = solver.solve(model)
    
    ### OUTPUT ###
    model.load(result)
    
    if (result.solver.status == SolverStatus.ok) and (result.solver.termination_condition == TerminationCondition.optimal):
    
        # note that we're using f-strings for output here which is a little different and cleaner than in the video
        growth = 100*model.growth()
        
        hiring = np.zeros(70)
        
        for i in range(70):
            hiring[i] = np.round(model.x[i]())
        hiring_mtx = np.reshape(hiring, (10,7))
        hiring_df = pd.DataFrame(hiring_mtx, columns=stage_name)
        
        hiring_A = int(sum(hiring_df['Associate']))
        hiring_C = int(sum(hiring_df['Consultant']))
        hiring_SC = int(sum(hiring_df['Senior Consultant']))
        hiring_M = int(sum(hiring_df['Manager']))
        hiring_SM = int(sum(hiring_df['Senior Manager']))
        hiring_AP = int(sum(hiring_df['Associate Partner']))
        hiring_P = int(sum(hiring_df['Partner']))
        
        ret_set = [growth, hiring_A, hiring_C, hiring_SC, hiring_M, hiring_SM, hiring_AP, hiring_P]
    else:
        ret_set = [0, 0, 0, 0, 0, 0, 0, 0]
    return ret_set
    
#################### Main logic ##############################

hire_range_junior = np.arange(start=0, stop=20, step=1)
hire_range_manager = np.arange(start=0, stop=10, step=1)
hire_range_partner = np.arange(start=0, stop=4, step=1)

hire_range_list = [
        hire_range_junior,  #Associate, Consultant, Senior Consultant
        hire_range_manager, #Manager, Manager, Senior Manager
        hire_range_partner  #Associate Partner, Partner
    ]

xref_max_hire_list = list(itertools.product(*hire_range_list))

# =============================================================================
# ratio_hc_list = [
#     [2,2,2.5,2,2], #default
#     [3,3,2.5,2,2],
#     [4,4,2.5,2,2],
#     [5,5,2.5,2,2],
#     [5,5,3,3,3]]
# =============================================================================


ratio_df = pd.DataFrame(columns=['max_hire_ast', 
                                 'max_hire_con', 
                                 'max_hire_sc', 
                                 'max_hire_m', 
                                 'max_hire_sm', 
                                 'max_hire_ap',
                                 'max_hire_p',
                                 'Growth_estimate',
                                 'Hire_A_estimate',
                                 'Hire_C_estimate',
                                 'Hire_SC_estimate',
                                 'Hire_M_estimate',
                                 'Hire_SM_estimate',
                                 'Hire_AP_estimate',
                                 'Hire_P_estimate'
                                 ])

for ind in range(len(xref_max_hire_list)):
    
    max_hire = xref_max_hire_list[ind]
    
    ratio_hc = [2,
                3.2,
                2,
                4,
                2,
                2]
    #Maximum number of hiring for each position per cycle
    bond_hire = [   (0,max_hire[0]), #Associate
                    (0,max_hire[0]), #Consultant
                    (0,max_hire[0]), #Senior Consultant
                    (0,max_hire[1]), #Manager
                    (0,max_hire[1]), #Senior Manager
                    (0,max_hire[2]), #Associate Partner
                    (0,max_hire[2])  #Partner
                    ]
    

    ret_list = optimize_hiring(ratio_hc, bond_hire, tran_list) 
    
    ratio_df.loc[ind, 'max_hire_ast']= bond_hire[0]
    ratio_df.loc[ind, 'max_hire_con']= bond_hire[1]
    ratio_df.loc[ind, 'max_hire_sc']= bond_hire[2]
    ratio_df.loc[ind, 'max_hire_m']= bond_hire[3]
    ratio_df.loc[ind, 'max_hire_sm']= bond_hire[4]
    ratio_df.loc[ind, 'max_hire_ap']= bond_hire[5]
    ratio_df.loc[ind, 'max_hire_p']= bond_hire[6]
    
    
    ratio_df.loc[ind, 'Growth_estimate']= ret_list[0]
    ratio_df.loc[ind, 'Hire_A_estimate'] = ret_list[1]
    ratio_df.loc[ind, 'Hire_C_estimate'] = ret_list[2]
    ratio_df.loc[ind, 'Hire_SC_estimate'] = ret_list[3]
    ratio_df.loc[ind, 'Hire_M_estimate'] = ret_list[4]
    ratio_df.loc[ind, 'Hire_SM_estimate'] = ret_list[5]
    ratio_df.loc[ind, 'Hire_AP_estimate'] = ret_list[6]
    ratio_df.loc[ind, 'Hire_P_estimate'] = ret_list[7]
    


ratio_df.to_csv(out_dir + '/sensitive_analysis_max_hire.csv', index = False)