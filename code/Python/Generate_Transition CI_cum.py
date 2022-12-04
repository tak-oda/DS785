### This code is to generate confidence interval of transition probability

import numpy as np
import pandas as pd
import re
import math

### PROBLEM DATA ###

### setup ###
file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"
out_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"

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
        tran_p = float(buf[1])
        lower = float(buf[3])
        upper = float(buf[4])
        n_risk = int(buf[5])
        n_remain = int(buf[6])
        

        dict_ci = dict()
        dict_ci['cycle'] = cur_cycle
        dict_ci['from_stage'] = from_stage
        dict_ci['to_sage'] = to_stage
        dict_ci['estimate'] = tran_p
        dict_ci['lower'] = lower
        dict_ci['upper'] = upper
        dict_ci['n.risk'] = n_risk
        dict_ci['n.remain'] = n_remain

        ci_list.append(dict_ci)
        

msSrv.close()

#Save df to file
ci_df = pd.DataFrame(ci_list)
ci_df.to_csv(out_dir + '/msSrv_ci_cum.csv', index = False)

