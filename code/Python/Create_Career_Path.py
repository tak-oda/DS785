import os
import pandas as pd
from datetime import date
import re

file_dir="C:/takeshi/Self_Study/UW/2022_Capstone/code/data/LinkedIn"
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
    
def format_ym(duration):
    parts = duration.split("–")
    if len(parts) > 1:
        fromYM = parts[0]
        toYM = parts[1]
    else:
        fromYM = parts[0]
        toYM = fromYM
    
    parts_from = fromYM.split()
    if len(parts_from) > 1:
        fromYear = parts_from[1]
        fromMonth = format_m (parts_from[0])
    else:
        fromYear = parts_from[0]
        fromMonth = "01"
        
    parts_to = toYM.split()
    if parts_to[0] == "Present":
        todays_date = date.today()
        toYear = str(todays_date.year)
        if len(str(todays_date.month)) > 1:
            toMonth = str(todays_date.month)
        else:
            toMonth = "0" + str(todays_date.month)
    elif len(parts_to) ==1:
        toYear = parts_to[0]
        toMonth = "01"
    else:
        toYear = parts_to[1]
        toMonth = format_m(parts_to[0])
    
    
    return [fromYear + fromMonth, toYear +  toMonth]
    

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


files = os.listdir(file_dir)
graphList = list()
idx = 1

p_yrsmos = re.compile(r'[a-zA-Z0-9\-·]*([0-9]yr)s*')
#p_yrsmos2 = re.compile(r'[a-zA-Z0-9\-·]*([0-9]mo)s*')
p_yrsmos2 = re.compile(r'[a-zA-Z0-9\-·]*([0-9]mo)s*$')

graphList = list()


for file in files:
    
    if file.find(".txt") < 0 :
        continue
    f  = open(file_dir + "/" + file, encoding="UTF-8")
    lines = f.readlines()
    hist_itm = list()
    
    cur_postn = ""
    prv_postn = ""
    wrk_postn = ""
    cur_comp = ""
    
    cur_dur_from = ""
    cur_dur_to = ""
    
    buf_comp_list = list()
    
    graph1 = dict()
    
    is_experience = False
    is_education = False
    is_skill = False
    
    cur_row = ""
    prv_row = ""
    prv2_row = ""
    
    cur_attr = ""
    prv_attr = "" #Previous attribute type
    # exp : Experience (header)
    # logo
    # comp_nm: Company Name
    # title
    # cntrct: Full-time or Contract
    # dur
    
    total_months_in_comp = 0 #Total months spent in the same company
    cum_months_in_comp = 0 #Cummulative months spent in the same company
    
    has_multi_pos_same_comp = False #if there are multiple positions experienced in the same employer
    
    
    for line in lines:
        cur_row = line
        cur_row = cur_row.replace('\n', '')
        half1 = cur_row[0: round(len(cur_row)/2)]
        half2 = cur_row[round(len(cur_row)/2) : ]
        
        if half1 == half2:
            cur_row = half1
        
        
        if cur_row.find("Experience" ) >= 0:
            cur_attr = "exp"
            is_experience = True
            
            #buf_comp_list.append(line[12:].replace('\n', ''))
        
  
        if is_experience == False:
            continue
        
        if cur_row.find("Education" ) >= 0:
            break
        
        if is_experience == True:
            
            buf = cur_row.replace(' ' ,'')

            matched = p_yrsmos.match(buf)
            matched2 = p_yrsmos2.match(buf)
            
            if  (matched is not None or matched2 is not None) and len(cur_row) < 40 : #Duration of position
                if buf.find("·") >=0 and buf.find("Full-time") < 0 : #duration by position
                    dur1 = buf.split("·")[0]
                    dur2 = cur_row.split("·")[1]
                    strt_ym = dur1.split("-")[0]
                    strt_ym = strt_ym.strip()
                    if len(dur1.split("-")) > 1:
                        end_ym = dur1.split("-")[1]
                        end_ym = end_ym.strip()
                    else:
                        end_ym = strt_ym
                    
                    if has_multi_pos_same_comp == True:
                        if prv_row == "Full-time" or prv_row == "Contract" or prv_row == "Part-time":
                            cur_postn = prv2_row
                        else:
                            cur_postn = prv_row
                        
                        #Evaluate if this is the last occurence in the same company
                        cum_months_in_comp = cum_months_in_comp + get_month_count(dur2)
                            
                        #If this is the last occurence, set has_multi_pos_same_comp false
                        if cum_months_in_comp >= total_months_in_comp:
                            has_multi_pos_same_comp = False
                            cum_months_in_comp = 0
                            
                        
                    else:
                        if prv_row == "Full-time" or prv_row == "Contract" or prv_row == "Part-time":
                            cur_comp = prv2_row
                            cur_postn = prv3_row
                        else:
                            cur_comp = prv_row  
                            cur_postn = prv2_row
                    
                    #print(file + "," + strt_ym + "-" + end_ym + "," + cur_comp + "/" + cur_postn)
                    
                    graph1 = dict()
                    graph1['file'] = file
                    graph1['company'] = cur_comp
                    graph1['position'] = cur_postn
                    graph1['start_ym'] = strt_ym
                    graph1['end_ym'] = end_ym
                    graphList.append(graph1)
                        
                    
                else:  #duration multiple positions
                    #set previous low to current company
                    has_multi_pos_same_comp = True
                    cur_comp = prv_row
                    cur_postn = ""
                    
                    #Extract # of year and # of month
                    if len(cur_row.split("·")) == 1:
                        cur_row = cur_row.split("·")[0]
                    else:
                        cur_row = cur_row.split("·")[1]
                    total_months_in_comp = get_month_count(cur_row)
                    #print(cur_comp + "/" + cur_postn)
                    
        prv3_row = prv2_row
        prv2_row = prv_row
        prv_row = cur_row
                

f.close()



df = pd.DataFrame(graphList)
df.to_csv(out_dir + '/career_path_DelloiteDigital_UK.csv', index = False)