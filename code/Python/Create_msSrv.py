import os
import pandas as pd
from datetime import date
from datetime import datetime


from dateutil import relativedelta

import re

file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/CareerPath"
out_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/CareerPath"


def get_month_count(duration):
    dur = duration.strip().split(" ")
    #print(dur)
    if duration.find("yr") >= 0 and duration.find("mo") >=0:
        n_year = dur[0]
        n_month = dur[2]
        total_months_in_comp = int(n_year)*12 + int(n_month)
    elif duration.find("yr") >= 0 and duration.find("mo") < 0:  
        n_year = dur[0]
        total_months_in_comp = int(n_year)*12
    elif duration.find("yr") < 0 and duration.find("mo") >= 0:
        n_month = dur[0]
        total_months_in_comp =  int(n_month)
    return total_months_in_comp
    

def get_duration(row):
    cur_month = "Jan2022"
    
    start = row['start_ym']
    end = row['end_ym']
    
    if end == "Present":
        end = cur_month
    
    
    
    start_mtn = start[0:3]
    end_mth = end[0:3]
    
    start_ymd = start[3:] + format_m(start_mtn) + '01'
    end_ymd = end[3:] + format_m(end_mth) + '01'
    
    #print ( start + " ->" + end )
    
    start_dt = datetime.strptime(start_ymd, '%Y%m%d')
    end_dt = datetime.strptime(end_ymd, '%Y%m%d')
    
    r = relativedelta.relativedelta(end_dt, start_dt)
    dur = (r.years * 12) + r.months + 1

    row['dur'] = dur
    row['start_ymd'] = start_ymd
    row['end'] = end_ymd
    
    #print ( start + "-" + end + "=" + str(dur))
    
    return row
    
def get_id(row):
    row['id'] = str(int(row['file'].replace('.txt', '')))
    return row

def format_m(month):
    
    if month == "Jan":
        return "01"
    elif month == "Feb":
        return "02"
    elif month =="Mar":
        return "03"
    elif month == "Apr":
        return "04"
    elif month == "May":
        return "05"
    elif month == "Jun":
        return "06"
    elif month == "Jul":
        return "07"
    elif month == "Aug":
        return "08"
    elif month == "Sep":
        return "09"
    elif month == "Oct":
        return "10"
    elif month == "Nov":
        return "11"
    elif month == "Dec":
        return "12"
    else:
        return "NA"






file = "career_path_DelloiteDigital_UK_Positions.csv"

    
df = pd.read_csv(file_dir + "/" + file, encoding="utf-8")


df = df.apply(get_duration, axis=1)

df = df.apply(get_id, axis=1)





df = df.sort_values(by=['file', 'start_ymd'])
df.to_csv(out_dir + '/career_path_DelloiteDigital_UK_dur.csv', index = False)


#Looping the rows to generate msSuv data set

stage_dict = {'Associate': 1, 
              'Consultant' :2, 
              'Senior Consultant' : 3,
              'Manager': 4,
              'Senior Manager' :5,
              'Assocaite Partner' : 6,
              'Partner': 7,
              'Exit' : 8
}

cur_id = "0"
start_stage_str = ""
end_stage_str = ""
start_stage = 0
end_stage = 0
stop = 0

prv_row = None

msSrv_buf = dict()
msSrv_list = list()
accum_dur = 0

for index, row in df.iterrows():
    if cur_id != row['id'] : #Changed individual
        if cur_id != "0":   
            
            start_stage_str = prv_row['Classification']
            if prv_row['end_ym'] == "Present":
                end_stage_str = "Right-Censored"
                end_stage = 0
            else:
                end_stage_str = "Exit"
                end_stage = stage_dict[end_stage_str]
            
            start_stage_str = prv_row['Classification']
            start_stage = stage_dict[start_stage_str]
            msSrv_buf = dict()
            msSrv_buf['id'] = cur_id
            msSrv_buf['stop'] = accum_dur
            msSrv_buf['start.stage'] = start_stage
            msSrv_buf['end.stage'] = end_stage
            msSrv_buf['start.stage_str'] = start_stage_str
            msSrv_buf['end.stage_str'] = end_stage_str
            
            #Add warning if start and end are same
            if start_stage_str == end_stage_str:
                msSrv_buf['note'] = "Looped link"
            else:
                msSrv_buf['note'] = ""
            
            msSrv_list.append(msSrv_buf)
            
            
            
            accum_dur = row['dur']
        else:
            accum_dur = accum_dur + row['dur']
            
        
        cur_id = row['id']
        
    else:
        start_stage_str = prv_row['Classification']
        end_stage_str = row['Classification']
        
        start_stage = stage_dict[start_stage_str]
        end_stage = stage_dict[end_stage_str]
        stop = accum_dur
        msSrv_buf = dict()
        msSrv_buf['id'] = cur_id
        msSrv_buf['stop'] = stop
        msSrv_buf['start.stage'] = start_stage
        msSrv_buf['end.stage'] = end_stage
        msSrv_buf['start.stage_str'] = start_stage_str
        msSrv_buf['end.stage_str'] = end_stage_str
        
        #Add warning if start and end are same
        if start_stage_str == end_stage_str:
            msSrv_buf['note'] = "Looped link"
        else:
            msSrv_buf['note'] = ""
                
        msSrv_list.append(msSrv_buf)
        
        accum_dur = accum_dur + row['dur']

    prv_row = row

#Save df to file
msSrv_df = pd.DataFrame(msSrv_list)
msSrv_df.to_csv(out_dir + '/career_path_DelloiteDigital_UK_msSrv.csv', index = False)



