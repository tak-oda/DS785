### This code is to generate confidence interval of transition probability

import numpy as np
import pandas as pd
import re
import math

### PROBLEM DATA ###

### setup ###
file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"
out_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"

### PROBLEM DATA ###

# load data transition matrix
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

tran_list = [tran1,tran2,tran3,tran4,tran5,tran6,tran7,tran8,tran9,tran10 ]

# load data msSrv summary output to get n.Risk
msSrv = open(file_dir + "/msSrv_status.txt", encoding="UTF-8")
lines = msSrv.readlines()


ci_list = list()
cur_cycle = 1
from_stage = 1
to_stage = 1

alpha = 1.96

for line in lines:
    
    if line.find("Transition") >= 0:
        buf = line.strip().split(" ")
        from_stage = int(buf[1])
        to_stage = int(buf[3])
    elif line.find("time") >= 0:
        pass
    elif len(line.strip()) == 0:
        pass
    else:
        buf = re.sub('\\s+', ' ', line.strip()).split(" ")
        cur_cycle = int(int(buf[0])/6)
        n_risk = int(buf[5])
        
        #Calculate lower and upper confidence interval
        tran_p = tran_list[cur_cycle-1].iloc[from_stage-1, to_stage]
        lower = tran_p - alpha * math.sqrt(tran_p * (1-tran_p) / n_risk)
        upper = tran_p + alpha * math.sqrt(tran_p * (1-tran_p) / n_risk)
        sd =  math.sqrt(tran_p * (1-tran_p) / n_risk)
        cv =  math.sqrt(tran_p * (1-tran_p) / n_risk) / tran_p
        
        dict_ci = dict()
        dict_ci['cycle'] = cur_cycle
        dict_ci['from_stage'] = from_stage
        dict_ci['to_sage'] = to_stage
        dict_ci['estimate'] = tran_p
        dict_ci['lower'] = lower
        dict_ci['upper'] = upper
        dict_ci['sd'] = sd
        dict_ci['cv'] = cv #Coefficient of Variation
        ci_list.append(dict_ci)
        

msSrv.close()

#Save df to file
ci_df = pd.DataFrame(ci_list)
ci_df.to_csv(out_dir + '/msSrv_ci.csv', index = False)

