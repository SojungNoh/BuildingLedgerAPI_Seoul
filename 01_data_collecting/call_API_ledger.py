import os
import numpy as np
import pandas as pd
import time

# Data Parsing
import requests
import urllib
from bs4 import BeautifulSoup

# Input
from input_gen import land_code_list, dong_dict, land_code2name

"""
Call data from Building Ledger API. 
Call unit : per Operation / Gu
"""

# Types of Building Ledger
operations = ['getBrBasisOulnInfo', 'getBrRecapTitleInfo', 'getBrTitleInfo', 'getBrFlrOulnInfo', 'getBrAtchJibunInfo', 'getBrExposPubuseAreaInfo', 'getBrWclfInfo', 'getBrHsprcInfo', 'getBrExposInfo', 'getBrJijiguInfo']

def dataframe_item(item):
    """Make dataframe per item"""
    
    # retrieve information from each tag
    per_item = item.find_all()
    tag_values = [per_item[i].get_text() for i in range(len(per_item))]
    tag_names = [per_item[i].name for i in range(len(per_item))]
    dataframe_item = pd.DataFrame(zip(tag_names, tag_values)).set_index(0).transpose()
    
    return dataframe_item


def dataframe_items(items):
    """
    Make dataframe per page, which includes multiple number of items
    The index for this dataframe is 'mgmBldrgstPk' which is the unique code for each real-estate
    """
    data = []
    for i in items:
        data.append(dataframe_item(i))

    return pd.concat(data).set_index('mgmBldrgstPk')


def dataframe_page(operation, land_code, dong_code, pn, serviceKey):
    """Call API, and make the page into a dataframe"""
        
    # Retrieve dataframe per page
    url_page = f'http://apis.data.go.kr/1613000/BldRgstService_v2/{operation}?sigunguCd={land_code}&bjdongCd={dong_code}&numOfRows={1000}&pageNo={pn}&ServiceKey={serviceKey}'
    try:
        webpage = requests.get(url_page)
        soup = BeautifulSoup(webpage.text, "lxml-xml")
        items = soup.select('item')
        dataframe_per_page = dataframe_items(items)
        
        return dataframe_per_page
    
    except:
        print(f"Error @{str(operation)}, check API url : {url_page}")
    
    


def max_pg_number(operation, land_code, dong_code, serviceKey):
    """Figure out the maximum number of the page to iterate."""
    
    # Request API to calculate 'item_count', this is to calculate 'max_pn'
    url = f'http://apis.data.go.kr/1613000/BldRgstService_v2/{operation}?sigunguCd={land_code}&bjdongCd={dong_code}&numOfRows={1000}&ServiceKey={serviceKey}'
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, "lxml-xml")
    item_count = int(soup.select('totalCount')[0].get_text())
    
    # Check if page number is within the limit
    max_pn = (item_count // 1000) + 1 #limit
    
    return max_pn


def dataframe_dong(operation, land_code, dong_code, serviceKey):
    """Retrieve information from a single 'dong'."""
    
    dataframes_dong = []
    max_pn = max_pg_number(operation, land_code, dong_code, serviceKey)
    
    for pn in range(1, max_pn+1):
        # call API and get Dataframe
        data = dataframe_page(operation, land_code, dong_code, pn, serviceKey)
        dataframes_dong.append(data)
        time.sleep(2)
        
    dataframe = pd.concat(dataframes_dong)

    return dataframe


def dataframe_gu(operation, land_code, serviceKey):
    """Retrieve information from a single 'gu'."""
    start = time.time()
    print("Start operation on {}".format(operation))
    dataframes_gu = []

    for i in range(len(dong_dict[str(land_code)])):
        dong_code = int(dong_dict[str(land_code)][i])
        data = dataframe_dong(operation, land_code, dong_code, serviceKey)
        dataframes_gu.append(data)
        time.sleep(2)
        print(f"Process {((i+1)/len(dong_dict[str(land_code)]))*100 : .2f}% Complete!")
        
    dataframe = pd.concat(dataframes_gu)
    
    end = time.time()
    dataframe.to_csv("..\\00_data\\building_ledger\\{}\\{}.csv".format(land_code2name[str(land_code)], land_code2name[str(land_code)] + "_" + str(operation)))
    print(f"{end - start : .2f} sec consumed")
    
    return dataframe