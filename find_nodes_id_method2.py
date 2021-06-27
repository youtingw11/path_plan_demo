import overpy
import googlemaps
from datetime import datetime, timedelta
import json
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd

# fx. of querying overpass API to get way info.
def query_overpass(lat, lon):    
    api = overpy.Overpass()

    result = api.query(        
        f"""
        (
        node
        ["highway" = 'traffic_signals'](around:10,{lat},{lon});           
        
        );
        
        (
          ._;
          >;
        );
        out;
      """
    )
    return result

# fx. of getting ways of each intersection
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

#initial data setting
gmaps = googlemaps.Client(key=' ')
geocode_origin = gmaps.geocode('taiwan 10617')
geocode_destination = gmaps.geocode('taipei train station')
print('Address of starting point: '+ geocode_origin[0]["formatted_address"]) 
print('Coordinate: (%s, %s)\n'%(geocode_origin[0]["geometry"]["location"]["lng"],geocode_origin[0]["geometry"]["location"]["lat"])) 
print('Address of destination: '+ geocode_destination[0]["formatted_address"])
print('Coordinate: (%s, %s)\n'%(geocode_destination[0]["geometry"]["location"]["lng"],geocode_destination[0]["geometry"]["location"]["lat"])) 

#Check the Distance Between Locations
distance_result = gmaps.distance_matrix(origins = geocode_origin[0]['formatted_address'], 
                      destinations = geocode_destination[0]["formatted_address"], 
                      departure_time = datetime.now() + timedelta(minutes=10))

#Get Directions Between Locations                  
directions_result = gmaps.directions(geocode_origin[0]['formatted_address'],
                                     geocode_destination[0]["formatted_address"],
                                     mode = "driving",
                                     alternatives = True,
                                     #language = "zh-TW",
                                     #avoid = "highways",

                                     arrival_time = datetime.now() + timedelta(minutes=0.5))                  
result = json.dumps(directions_result, sort_keys = True, indent = 1)
print("-----------------------------------------")

#print results of path
import datetime
step_coordinates = []
all_information = pd.DataFrame() # lat, lon, traveling time, distance
distance = []
trav_time = []
for k in range(len(directions_result)):
    
    #informations of every path
    print("< path", k+1, ">")    
    for i, leg in enumerate(directions_result[k]["legs"]):
        print("Starting point:",
            leg["start_address"],
            "\nDestination:",
            leg["end_address"], 
            "\nDistance:",  
            leg["distance"]["value"]/1000,"km", 
            "\nTraveling Time: ",
            str(datetime.timedelta(seconds = leg["duration"]["value"]))
        )
        distance.append(leg["distance"]["value"])
        trav_time.append(datetime.timedelta(seconds = leg["duration"]["value"]))
        
    #print every steps (expect the last step)  
    move_list = []
    steps = directions_result[k]['legs'][0]['steps']  
    for i in range(len(steps)-1):
        print("Step",i,"==>",str(steps[i]['html_instructions']).split("<div ",1)[0].replace("<b>","").replace("</b>","").replace("<wbr/>",""))
        
        try:
            print(str(steps[i]["maneuver"]))
            move_list.append(str(steps[i]["maneuver"]))  
        except:
            move_list.append('none')
        
    print("-----------------------------------------")     
    
    # get coordinates of each step (expect the last step)  
    steps = directions_result[k]['legs'][0]['steps']
    coor = []
    lat = []
    lon = []
    for j in range(len(steps)-1):
        coor.append([steps[j]['end_location']['lat'], steps[j]['end_location']['lng']])
                     
        lat.append(steps[j]['end_location']['lat'])
        lon.append(steps[j]['end_location']['lng'])
    step_coordinates.append(np.asarray(coor))
    
    all_information = pd.concat([all_information, pd.DataFrame({'lat_%s'%(k):lat})], axis=1)
    all_information = pd.concat([all_information, pd.DataFrame({'lon_%s'%(k):lon})], axis=1)
    all_information = pd.concat([all_information, pd.DataFrame({'round_%s'%(k):move_list})], axis=1)


# find ways of each intersection of each path
node_id = []
all_way = pd.DataFrame()
# find nodes
for i in range(np.size(step_coordinates)):
    n =[]
    for j in range(np.size(step_coordinates[i],0)):   
        res = query_overpass(step_coordinates[i][j][0], step_coordinates[i][j][1])
        if res.node_ids != []:
            n.append(str(res.node_ids[0]))
        else:
            n.append('none')
    node_id.append(n)
    print('node index of path %s: %s'%(i+1, n))

    # find ways and store to the dataframe
    df1 = pd.DataFrame({'%s'%(k):find_intersection(n)})
    all_way = pd.concat([all_way, df1], ignore_index=True, axis=1)


# merge data of distance and traveling time    
all_information = pd.concat([all_information, pd.DataFrame({'distance':distance})], axis=1)
all_information = pd.concat([all_information, pd.DataFrame({'trav_time':trav_time})], axis=1)

#output to the .csv file
all_way.to_csv('second_data.csv', index = False)
all_information.to_csv('second_information.csv', index = False)
