import os
import pandas as pd
from datetime import date
from datetime import datetime


from dateutil import relativedelta

import re

file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/CareerPath"
out_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/CareerPath"




file = "career_path_DelloiteDigital_UK_msSrv.csv"

    
df = pd.read_csv(file_dir + "/" + file, encoding="utf-8")


cur_id = "0"



prv_row = None

msSrv_buf = dict()
msSrv_list = list()

abs_idx = 1
idx = 0
    
for index, row in df.iterrows():
    if cur_id != row['id'] : #Changed individual
            
        idx = 0
        msSrv_buf = dict()
        msSrv_buf['id'] = abs_idx
        msSrv_buf['id_org'] = row['id']
        msSrv_buf['sub_id'] = row['id']*10000+ idx
        msSrv_buf['stop'] = row['stop']  
        msSrv_buf['start.stage'] = row['start.stage']
        msSrv_buf['end.stage'] = row['end.stage']
        msSrv_buf['start.stage_str'] = row['start.stage_str']
        msSrv_buf['end.stage_str'] = row['end.stage_str']
        msSrv_buf['note'] = row['note']
        
        msSrv_list.append(msSrv_buf)
        
        idx = idx + 1
        abs_idx = abs_idx + 1
        cur_id = row['id']
        
    else:

        msSrv_buf = dict()
        msSrv_buf['id'] = abs_idx
        msSrv_buf['id_org'] = row['id']
        msSrv_buf['sub_id'] = row['id']*10000 + idx
        msSrv_buf['stop'] = row['stop']  - prv_row['stop'] + 1
        msSrv_buf['start.stage'] = row['start.stage']
        msSrv_buf['end.stage'] = row['end.stage']
        msSrv_buf['start.stage_str'] = row['start.stage_str']
        msSrv_buf['end.stage_str'] = row['end.stage_str']
        msSrv_buf['note'] = row['note']
        
        msSrv_list.append(msSrv_buf)
        
        idx = idx + 1
        abs_idx = abs_idx + 1
        cur_id = row['id']

    prv_row = row

#Save df to file
msSrv_df = pd.DataFrame(msSrv_list)
msSrv_df.to_csv(out_dir + '/career_path_DelloiteDigital_UK_msSrv_relative.csv', index = False)



