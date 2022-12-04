### This code is Pyomo linear programming equivalent with Optimie_Hiring04.py

# 2022/07/03 Created
# 2022/08/14 Fixed issue that sum of transition probability becomes larger/less than one in case upper/lower boundary
# 2022/11/05 Added Senior Consultant - Manager ratio

from pyomo.environ import *
import numpy as np
import pandas as pd
import copy

### PROBLEM DATA ###

### setup ###
file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"
out_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/linear_programming"
debug_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/debug"

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

# Debug file
debug_t = pd.read_csv(debug_dir + "/debug_matrix.config")

# Confidence interval of Transition Probabilities
ci_df = pd.read_csv(file_dir + "/msSrv_ci.csv")

cycle =  [1,2,3,4,5,6,7,8,9,10] #5 years cycle
stage = [1,2,3,4,5,6,7]
stage_with_exit = [1,2,3,4,5,6,7, 8] #for recalculation of transition probability
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

#Head count ration
ratio_ast_mng = 2
ratio_con_mng = 2
ratio_sc_mng = 1
ratio_mng_sm = 2
ratio_mng_pt = 2.5
ratio_sm_pt = 2
ratio_sm_ap = 2

#Optimize hiring 
#Var: tran_list: transition matrix
#Return: Growth rate and total number of hiring from position A to P
def optimize_hiring(tran_list):

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
        
        # model.fte_ratio.add( expr = ast_fte -2*mng_fte  >= 0 )
        # model.fte_ratio.add( expr = con_fte -2*mng_fte  >= 0 )
        # model.fte_ratio.add( expr = mng_fte -2*sm_fte  >= 0 )
        # model.fte_ratio.add( expr = mng_fte -2.5* pt_fte  >= 0 )
        # model.fte_ratio.add( expr = sm_fte  -2*pt_fte  >= 0 )
        # model.fte_ratio.add( expr = sm_fte  -2*ap_fte  >= 0 )
        
        model.fte_ratio.add( expr = ast_fte -1*ratio_ast_mng*mng_fte  >= 0 )
        model.fte_ratio.add( expr = con_fte -1*ratio_con_mng*mng_fte  >= 0 )
        model.fte_ratio.add( expr = sc_fte  -1*ratio_sc_mng*mng_fte  >= 0 )
        model.fte_ratio.add( expr = mng_fte -1*ratio_mng_sm*sm_fte  >= 0 )
        model.fte_ratio.add( expr = mng_fte -1*ratio_mng_pt*pt_fte  >= 0 )
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
    
    if (result.solver.status == SolverStatus.ok) and (result.solver.termination_condition == TerminationCondition.optimal):
        ### OUTPUT ###
        
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

ci_df['Growth_estimate']=0
ci_df['Growth_lower']=0
ci_df['Growth_upper']=0
ci_df['Hire_A_estimate']=0
ci_df['Hire_A_lower']=0
ci_df['Hire_A_upper']=0
ci_df['Hire_C_estimate']=0
ci_df['Hire_C_lower']=0
ci_df['Hire_C_upper']=0
ci_df['Hire_SC_estimate']=0
ci_df['Hire_SC_lower']=0
ci_df['Hire_SC_upper']=0
ci_df['Hire_M_estimate']=0
ci_df['Hire_M_lower']=0
ci_df['Hire_M_upper']=0
ci_df['Hire_SM_estimate']=0
ci_df['Hire_SM_lower']=0
ci_df['Hire_SM_upper']=0
ci_df['Hire_AP_estimate']=0
ci_df['Hire_AP_lower']=0
ci_df['Hire_AP_upper']=0
ci_df['Hire_P_estimate']=0
ci_df['Hire_P_lower']=0
ci_df['Hire_P_upper']=0


for ind in range(len(ci_df)):
    cycle = ci_df['cycle'][ind]
    from_stg = ci_df['from_stage'][ind]
    to_stg = ci_df['to_sage'][ind]
    
    estimate = ci_df['estimate'][ind]
    lower = ci_df['lower'][ind]
    upper = ci_df['upper'][ind]
    
    #Skip to analyze sensitivity if all the three statistics are equal
    if estimate == lower and estimate == upper:
        continue
    
    #Set debug flag
    debug = False
    if len(debug_t.loc[ (debug_t['cycle']==cycle ) & (debug_t['from_stage'] == from_stg) & (debug_t['to_stage']==to_stg)]) > 0:
        debug = True
    
    #Execute optimize function with estimate
    buf_tran_list = copy.deepcopy(tran_list) #Preserve original trans prob
    ret_list = optimize_hiring(buf_tran_list)
    
    ci_df.loc[ind, 'Growth_estimate']= ret_list[0]
    ci_df.loc[ind, 'Hire_A_estimate'] = ret_list[1]
    ci_df.loc[ind, 'Hire_C_estimate'] = ret_list[2]
    ci_df.loc[ind, 'Hire_SC_estimate'] = ret_list[3]
    ci_df.loc[ind, 'Hire_M_estimate'] = ret_list[4]
    ci_df.loc[ind, 'Hire_SM_estimate'] = ret_list[5]
    ci_df.loc[ind, 'Hire_AP_estimate'] = ret_list[6]
    ci_df.loc[ind, 'Hire_P_estimate'] = ret_list[7]
    
    #Execute optimize function with lower
    
    buf_tran_list = copy.deepcopy(tran_list) #Preserve original trans prob
    
    if lower < 0:
        lower = 0
    #replace transition probability with lower boundary
    buf_tran_list[cycle-1].iloc[from_stg-1, to_stg] = lower
    
    
    #Adjust transition probability to other position in the same cycle (to make prob=1 for total)
    #Move extra probability to other transition. 
    #Add the extra to the other probabilities in the same probability matrix
    
    delta_lower  = estimate - lower
    
    prop_total = 1 - estimate
    for s in stage_with_exit:   
        if s != from_stg:
            #Calculate allocation amount based on proportion
            cur_prob = buf_tran_list[cycle-1].iloc[from_stg - 1, s]
            buf_tran_list[cycle-1].iloc[from_stg - 1, s] = cur_prob + delta_lower*(cur_prob/prop_total)
    
    ret_list = optimize_hiring(buf_tran_list)
    
    if debug == True:
        buf_tran_list[cycle-1].to_csv(debug_dir + '/sensitive_analysis_tran_prob_lower_' + str(cycle) + '.csv', index = False)
    
    ci_df.loc[ind, 'Growth_lower'] = ret_list[0]
    ci_df.loc[ind, 'Hire_A_lower'] = ret_list[1]
    ci_df.loc[ind, 'Hire_C_lower'] = ret_list[2]
    ci_df.loc[ind, 'Hire_SC_lower'] = ret_list[3]
    ci_df.loc[ind, 'Hire_M_lower'] = ret_list[4]
    ci_df.loc[ind, 'Hire_SM_lower'] = ret_list[5]
    ci_df.loc[ind, 'Hire_AP_lower'] = ret_list[6]
    ci_df.loc[ind, 'Hire_P_lower'] = ret_list[7]
    
    
    #Call function
    
    #Execute optimize function with upper
    buf_tran_list = copy.deepcopy(tran_list) #Preserve original trans prob
    #replace transition probability with upper boundary
    
    #If upper > 1 then set 1
    if upper > 1:
        upper = 1
    buf_tran_list[cycle-1].iloc[from_stg-1, to_stg] = upper
    
    
    #Adjust transition probability to other position in the same cycle (to make prob=1 for total)
    
    delta_upper  = upper - estimate 
    prop_total = 1 - estimate
    
    for s in stage_with_exit:   
        if s != from_stg:
            #Calculate allocation amount based on proportion
            cur_prob = buf_tran_list[cycle-1].iloc[from_stg - 1, s]
            buf_tran_list[cycle-1].iloc[from_stg - 1, s] = cur_prob - delta_upper*(cur_prob/prop_total)
    
    
    
    ret_list = optimize_hiring(buf_tran_list)
    
    if debug == True:
        buf_tran_list[cycle-1].to_csv(debug_dir + '/sensitive_analysis_tran_prob_upper_' + str(cycle) + '.csv', index = False)
  
    
    ci_df.loc[ind, 'Growth_upper'] = ret_list[0]
    ci_df.loc[ind, 'Hire_A_upper'] = ret_list[1]
    ci_df.loc[ind, 'Hire_C_upper'] = ret_list[2]
    ci_df.loc[ind, 'Hire_SC_upper'] = ret_list[3]
    ci_df.loc[ind, 'Hire_M_upper'] = ret_list[4]
    ci_df.loc[ind, 'Hire_SM_upper'] = ret_list[5]
    ci_df.loc[ind, 'Hire_AP_upper'] = ret_list[6]
    ci_df.loc[ind, 'Hire_P_upper'] = ret_list[7]

ci_df.to_csv(out_dir + '/sensitive_analysis_tran_prob.csv', index = False)