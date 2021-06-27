import googlemaps
from datetime import datetime, timedelta
import json
import pandas as pd
import datetime
import numpy as np
print('start time: %s'%(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

#資料處理: 將google_api抓下來之路徑清理至只剩路名
import re

def clear_en(needc: list ) -> list:
    a = []
    for i in needc:
        clear1 = re.sub('[a-zA-Z]', '', i).strip()
        clear2 = re.sub('5  ', '', clear1).strip()
        clear3 = re.sub('[().,]', '', clear2).strip()
        clear4 = re.sub(' ', '', clear3).lstrip()
        if clear4 != "":
            a.append(clear4)
        else:
            a.append('none')
    return a

#osm :利用osm找出無人車所會經過的各種道路之交集node_id
import overpy.helper
import re
import time
    
def find_intersection_id(all_i: list) -> list:
    intersection_id = []
    for i in range(len(all_i) - 1):
        if "/" in all_i[i]:
            all_i[i] = all_i[i].split("/")
    for i in range(len(all_i) - 1):
        if isinstance(all_i[i], str) and isinstance(all_i[i+1], str):
            intersection = overpy.helper.get_intersection(all_i[i],all_i[i+1],"3601293250")                            
            
            if intersection == []:
                intersection_id.append("none")
            else: 
                try:
                    b = str(intersection[0]).split(" ")
                    c = re.sub('id=', '', b[1]).strip()
                    intersection_id.append(c)

                except:
                    b = str(intersection)
                    c = re.sub('id=', '', b).strip()
                    intersection_id.append(c)

            time.sleep(1)
        elif isinstance(all_i[i], str) and isinstance(all_i[i+1], list):
            count = 0
            for j in range(len(all_i[i+1])):
                intersection = overpy.helper.get_intersection(all_i[i],all_i[i+1][j],"3601293250")
 
                if intersection != []:
                    count = 1
                    try:
                        b = str(intersection[0]).split(" ")
                        c = re.sub('id=', '', b[1]).strip()
                        intersection_id.append(c)

                        all_i[i+1] = all_i[i+1][j]   
                    except:
                        b = str(intersection)
                        c = re.sub('id=', '', b).strip()
                        intersection_id.append(c)

                        all_i[i+1] = all_i[i+1][j] 
                    break
            if count == 0:
                intersection_id.append("none")

                all_i[i+1] = all_i[i+1][0]
            time.sleep(1)
    print(intersection_id)
    return intersection_id

#爬蟲: 用node_id抓出經過路口的道路總數  
import requests
from bs4 import BeautifulSoup

def find_intersection(ids: list) -> list :
    intersection = []
    for x in ids:
        if x != "none":
            url = "https://www.openstreetmap.org/node/" + x
            re = requests.get(url)
            soup_id = BeautifulSoup(re.text,"html.parser")
            
            road = soup_id.find("summary")
            roads = road.text
            intersection.append(roads)
            
        else:
            intersection.append("0 ways")
    print(intersection)
    return intersection


#利用google geocoding api 找到起始位置及末位置之經緯度
gmaps = googlemaps.Client(key=' ')

geocode_origin = gmaps.geocode('taiwan 10617')
geocode_destination = gmaps.geocode('taipei train station')

print(geocode_origin[0]["formatted_address"]) 
print(geocode_origin[0]["geometry"]["location"]["lat"]) 
print(geocode_origin[0]["geometry"]["location"]["lng"])

print(geocode_destination[0]["formatted_address"]) 
print(geocode_destination[0]["geometry"]["location"]["lat"]) 
print(geocode_destination[0]["geometry"]["location"]["lng"])


#利用google distance_matrix api找到兩者間的距離
distance_result = gmaps.distance_matrix(origins = geocode_origin[0]['formatted_address'], 
                      destinations = geocode_destination[0]["formatted_address"], 
                      departure_time = datetime.datetime.now() + timedelta(minutes=10))
 

#利用google direction api 找到多條google map上的最佳路徑         
directions_result = gmaps.directions(geocode_origin[0]['formatted_address'],
                                     geocode_destination[0]["formatted_address"],
                                     mode = "driving",
                                     alternatives = True,
                                     #language = "zh-TW",
                                     avoid = "highways",
                                     arrival_time = datetime.datetime.now() + timedelta(minutes=0.5))                  

#利用json函式處理google api所回傳之json檔
result = json.dumps(directions_result, sort_keys = True, indent = 1)
print("-----------------------------------------")


import datetime

all_way = pd.DataFrame()
all_information = pd.DataFrame() # lat, lon, traveling time, distance
distance = []
trav_time = []
for k in range(3):
    #印出最佳路徑的詳細資訊
    print("< 最佳路徑", k+1, ">")
    for i, leg in enumerate(directions_result[k]["legs"]):
        print("起點:",
            leg["start_address"],
            "\n終點:",
            leg["end_address"], 
            "\ndistance:",  
            leg["distance"]["value"]/1000,"km", 
            "\ntraveling Time: ",
            str(datetime.timedelta(seconds = leg["duration"]["value"]))
        )
        distance.append(leg["distance"]["value"])
        trav_time.append(datetime.timedelta(seconds = leg["duration"]["value"]))
    
    
    #印出從起點到終點所需的各步驟 
    steps = directions_result[k]['legs'][0]['steps']
    need_clear = []
    move_list = []
    for i in range(len(steps)):
        print("Step",i,"==>",str(steps[i]['html_instructions']).split("<div ",1)[0].replace("<b>","").replace("</b>","").replace("<wbr/>",""))
        need_clear.append(str(steps[i]['html_instructions']).split("<div ",1)[0].replace("<b>","").replace("</b>","").replace("<wbr/>",""))        
        try:
            #print(str(steps[i]["maneuver"]))
            #print(str(steps[i]["end_location"]))
            move_list.append(str(steps[i]["maneuver"]))
        except:
            move_list.append('none') 
    
    # expect the last step
    move_list.pop()         
    #將處理後的資料丟進前面寫的函式中做運算，得到最終結果
    clear_instruction = clear_en(need_clear)
    print(clear_instruction)
    
    # get coordinates of each step (expect the last step)  
    steps = directions_result[k]['legs'][0]['steps']
    coor = []
    lat = []
    lon = []
    for j in range(len(steps)-1):
        coor.append([steps[j]['end_location']['lat'], steps[j]['end_location']['lng']])
        lat.append(steps[j]['end_location']['lat'])
        lon.append(steps[j]['end_location']['lng'])
    
    intersection_ids = find_intersection_id(clear_instruction)
    all_information = pd.concat([all_information, pd.DataFrame({'lat_%s'%(k):lat})], axis=1)
    all_information = pd.concat([all_information, pd.DataFrame({'lon_%s'%(k):lon})], axis=1)
    all_information = pd.concat([all_information, pd.DataFrame({'round_%s'%(k):move_list})], axis=1)
    
    #store to the dataframe
    df1 = pd.DataFrame({'%s'%(k):find_intersection(intersection_ids)})
    all_way = pd.concat([all_way, df1], ignore_index=True, axis=1)
    
    
    print("-----------------------------------------")
    
    
# merge data of distance and traveling time    
all_information = pd.concat([all_information, pd.DataFrame({'distance':distance})], axis=1)
all_information = pd.concat([all_information, pd.DataFrame({'trav_time':trav_time})], axis=1)

#output to the .csv file
all_way.to_csv('first_data.csv', index = False)
all_information.to_csv('first_information.csv', index = False)

print('\nfinish time: %s'%(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
