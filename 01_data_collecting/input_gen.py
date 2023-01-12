"""
# Input generating file for 'Data_Loader'

This file aims to generate list for two inputs to feed directly into 'data_loader.ipynb'. The two inputs for 'data_loader.ipynb' are:
1. **land_code** : Regional code of the target region,  
    - Scope : 11110 Jongro-gu ~ 11740 Gangdong-gu
2. **ymd** : 6 digits of Year-Month of the target period, 
    - Scoppe : 200601 ~
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')



# 1. land_code
def land_code_gen(korean_gov_reg_code_txt) :
    """
    Process txt file provided by the Korean Government in a API feedable form for each gu.
    Outputs:
    1. land_code - five digit landcode per 'Dong'.
    2. land_code2name - lookup for a land code.
    3. land_name2code - lookup for a land name.
    """
    # Filter codes corresponding to Seoul
    raw_data = pd.read_csv(korean_gov_reg_code_txt, sep='\t', encoding='cp949')
    raw_data = raw_data[raw_data['폐지여부'] == '존재']
    raw_data_seoul = raw_data[raw_data['법정동명'].str.contains('서울특별시')] # regional codes included in the boundary of Seoul
    raw_data_seoul['법정동코드'] = raw_data_seoul['법정동코드'].astype(str)
    raw_codes = list(raw_data_seoul['법정동코드'])
    
    # Retrieve first 5 digits from the column '법정동코드', since it is the requirement for API
    land_code = sorted(list(set([i[:5] for i in raw_codes])))[1:] # first index removed, since it represents 'city of Seoul'

    # dictionary for 'land_code' and its 'land_code_name'
    land_code_name = []
    for i in range(len(land_code)):
        name_raw = list(raw_data_seoul[raw_data_seoul['법정동코드'].str.contains(land_code[i] + '00000')]['법정동명'])[0]
        name_raw = name_raw.strip('서울특별시 ')
        land_code_name.append(name_raw)

    land_code2name = dict(zip(land_code, land_code_name))
    land_name2code = dict(zip(land_code_name, land_code))
    
    return land_code, land_code2name, land_name2code



# 2. ymd
def ymd_gen(current_year, current_month):
    """
    Generate timesteps to take into account in a API feedable form.
    Output: six digit timestep per month
    """
    years = [str(i) for i in range(2006, current_year+1)]
    mnths = [format(i, '02') for i in range(1, current_month+1)]

    ymd = []
    for y in range(len(years)):
        for m in range(len(mnths)):
            timestep = years[y] + mnths[m]
            ymd.append(timestep)
            
    return ymd



# 3. dong_dict
def dong_dict_gen(korean_gov_reg_code_txt):
    """ 
    Process txt file provided by the Korean Government in a API feedable form for each dong per gu.
    Output: five digit dong codes for each gu, which is a dictionary.
    """
    raw_data = pd.read_csv(korean_gov_reg_code_txt, sep='\t', encoding='cp949')
    raw_data = raw_data[raw_data['폐지여부'] == '존재']
    raw_data_seoul = raw_data[raw_data['법정동명'].str.contains('서울특별시')] # regional codes included in the boundary of Seoul
    raw_data_seoul['법정동코드'] = raw_data_seoul['법정동코드'].astype(str)
    raw_codes = list(raw_data_seoul['법정동코드'])

    # Retrieve first 5 digits from the column '법정동코드', since it is the requirement for API
    land_code = sorted(list(set([i[:5] for i in raw_codes])))[1:] # first index removed, since it represents 'city of Seoul'
    
    # Loop for every 'land_code' to retrieve 'dong_code'
    dong_dict = {}
    for i in range(len(land_code)):
        raw_data_gu = raw_data_seoul[raw_data_seoul['법정동명'].str.contains(land_code2name[land_code[i]])]
        raw_codes_gu = list(raw_data_gu['법정동코드'])
        dong_code = sorted(list(set([i[5:] for i in raw_codes_gu])))[1:]
        dong_dict[land_code[i]] = dong_code # append in dong_dict
    
    return dong_dict



# Data Generation

land_code_list, land_code2name, land_name2code = land_code_gen('법정동코드 전체자료.txt')
dong_dict = dong_dict_gen('법정동코드 전체자료.txt')
ymd_list = ymd_gen(2022, 12)