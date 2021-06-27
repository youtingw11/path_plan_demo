import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import googlemaps
import matplotlib.cm as cm

# fx. of calculating # of conflicts
def way_to_conflict(way_list, move_list):
    
    # fx. of transforming ways to confilcts 
    def confilct_calculate(x):
        return {
            # [corssing, merging, diverging]
            0: [0, 0, 0],
            1: [0, 0, 0],
            2: [0, 0, 0],
            3: [3, 3, 3],
            4: [16, 8, 8],
        }.get(x, [16, 8, 8]) 
    
    # weighting setting
    c_weight, m_weight, d_weight= 3, 2, 1    
    conflict, step_num, conflict_index, trun_num= [], [], [], []

    for i in range(np.size(way_list,1)):
        t = 0
        # neglect nan
        each_way = way_list[i].dropna()
        
        # calcluate conflicts of each step (in each type)
        c, m, d = 0, 0, 0
        for j in range(np.size(each_way)):            
            c = c + confilct_calculate(each_way[j])[0]
            m = m + confilct_calculate(each_way[j])[1]
            d = d + confilct_calculate(each_way[j])[2]
            
            # determine the round case or not
            if move_list[i][j] == 'roundabout-right':
                c = c - confilct_calculate(each_way[j])[0] + 0
                m = m - confilct_calculate(each_way[j])[1] + 0
                d = d - confilct_calculate(each_way[j])[2] + 8
                t = t+1
            # count the # of turn
            elif 'turn-' in move_list[i][j]:
                t = t + 1
                
        conflict.append([c, m, d])
        
        # calulate conflict index
        conflict_index.append(c*c_weight + m*m_weight + d*d_weight)
        
        # total steps and turn
        step_num.append(np.size(each_way))
        trun_num.append(t)
        
    return(step_num, conflict, conflict_index, trun_num)

# fx. of sorting out the data
def sort_information_data(first_raw_information):
    # time and distance
    distance_list = np.asarray(first_raw_information['distance'].dropna())
    time_list = np.asarray(first_raw_information['trav_time'].dropna())

    #lat., lon., and moves in each steps (endpoints)
    lat_list = []
    lon_list = []
    move_list = []
    for i in range(3):
        lat_list.append(np.asarray(first_raw_information['lat_%s'%(i)]))
        lon_list.append(np.asarray(first_raw_information['lon_%s'%(i)]))
        move_list.append(np.asarray(first_raw_information['round_%s'%(i)]))
        
    return(distance_list, time_list, lat_list, lon_list, move_list)

# fx. of output informations to the screen
def output_result(address_and_coor, distance_list, time_list, conflict_index_list, confilct_list, turn_list ):
    
    for i in range(np.size(distance_list)):
        print("\n--------------------------------------------------------------------------------------------------------------------")
        print("< Path %s >"%(i+1))
    
        # basic informations
        print("\n[Basic informations]")
        print('1. Address of starting point: '+ address_and_coor[0]) 
        print('   Coordinate: (%.4f, %.4f)'%(address_and_coor[2][0],address_and_coor[2][1])) 
        print('2. Address of destination: '+ address_and_coor[1])
        print('   Coordinate: (%.4f, %.4f)'%(address_and_coor[3][0],address_and_coor[3][1])) 
    
        # distance, time, and rate
        print('3. Distance: %.3f [km]'%(distance_list[i]/1000))
        print('4. Time: %.3f [min.]'%(time_list[i]))
        print('5. Rate: %.3f [km/hr.]'%(distance_list[i]/1000/time_list[i]*60))
        
        #conflict results
        print("\n[Conflict Analysis]")
        print('1. Conflict-point counts: ')
        print('   (1) corssing : %s'%(confilct_list[i][0]))
        print('   (2) merging  : %s'%(confilct_list[i][1]))
        print('   (3) diverging: %s'%(confilct_list[i][2]))
        print('   Total counts: %s'%(sum(confilct_list[i])))
        print('2. Conflict index: %s'%(conflict_index_list[i]))
        print('3. Turning counts: %s'%(turn_list[i]))
        print('4. Conflict index / Turning counts: %.3f'%(conflict_index_list[i] / turn_list[i]))     

#fx. of plot of comparison w/ confilct numbers in different methods
def plot_comparison_with_conflict(total_conflict_list, para, para_name, para_unit, ylim, line_color):
    '''
    input data of conflicts and data you want to comparison
    bar plot will be # of conflict in different methods
    line plot will be data you want to comparison
    '''
    
    method = ['path 1', 'path 2', 'path 3']
    fig,ax = plt.subplots(figsize=(7,5),dpi=150)
    
    #coor. of # of conflicts
    ax.bar([1, 2, 3], total_conflict_list, width=0.2, alpha=0.8,\
       color=['#7FD0E3', '#71B7DF','#799BD3'] )
    ax.set_ylim([0, 500])
    ax.set_ylabel('conflict index', fontsize = 12)
    
    # parameter
    ax2 = ax.twinx()
    ax2.plot([1, 2, 3], para, linewidth = 2.5,marker = 'o', color = line_color)
    ax2.set_ylim(ylim)
    ax2.set_ylabel('%s %s'%(para_name, para_unit), fontsize = 12)
    
    # other setting
    plt.xticks([1, 2, 3], method)
    plt.title('conflict index vs. %s'%(para_name), fontsize = 14)
    plt.tight_layout()
    plt.show()
    
    return()

# fx. of comparison in conflict types (corssing, merging, diverging) in different paths
def plot_conflict_type(confilct_list):

    method = ['path 1', 'path 2', 'path 3']
    fig,ax = plt.subplots(figsize=(7,5),dpi=150)
    color=['#D16BA5', '#86A8E7','#5FFBF1']
    
    #coor. of # of conflicts
    for i in range(np.size(confilct_list, 1)):
        ax.bar([1+5*i, 2+5*i, 3+5*i], confilct_list[i], width=0.6, alpha=0.8,\
               color = color )
        ax.set_ylim([0, 100])
        ax.set_ylabel('# of conflict points', fontsize = 12)    
        
        
    # other setting
    colors = {'corssing':color[0],'merging':color[1], 'diverging':color[2]}         
    labels = list(colors.keys())
    handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
    plt.legend(handles, labels, loc = 'upper left')
    plt.xticks([2, 7, 12], [method[0],method[1],method[2]])
    plt.title('Comparison in conflict types in different paths', fontsize = 14)
    plt.tight_layout()
    plt.show()

    return()

# fx. of plot of conflict index / turning counts  
def plot_conflict_turning(conflict_index_list, turn_list):

    method = ['path 1', 'path 2', 'path 3']
    fig,ax = plt.subplots(figsize=(7,5),dpi=150)
    color=['#D16BA5', '#86A8E7','#5FFBF1']
    
    #coor. of # of conflicts
    ax.bar([1, 2, 3],np.asarray(conflict_index_list)/np.asarray(turn_list), width=0.2, alpha=0.8,color = color)
    ax.set_ylim([0, 60])
    ax.set_ylabel('conflict index / turning counts', fontsize = 12)
        
        
    # other setting
    plt.xticks([1,2,3], [method[0],method[1],method[2]])
    plt.title('Conflict index per turning in different paths', fontsize = 14)
    plt.tight_layout()
    plt.show()
    
    return()

# fx. of confilct index distribution
def plot_conflict_distribution(data,lat_list, lon_list):

    # fx. of transforming ways to confilcts 
    def confilct_calculate(x):
        return {
            # [corssing, merging, diverging]
            0: [0, 0, 0],
            1: [0, 0, 0],
            2: [0, 0, 0],
            3: [3, 3, 3],
            4: [16, 8, 8],
        }.get(x, [16, 8, 8]) 
    
    # calculate conflict index in each points and plot
    lon = []
    lat = []
    con_idx = []
    for i in range(np.size(lat_list,0)):        
        for j in range(np.size(lat_list,1)):
            if np.isnan(lat_list[i][j]) == False:                
                lon.append(lon_list[i][j])
                lat.append(lat_list[i][j])
                con_idx.append(np.sum(confilct_calculate(data[i][j])))         
    
    #plot
    fig,ax = plt.subplots(figsize=(9,6),dpi=150)
    cm = plt.cm.get_cmap('coolwarm')
    plt.scatter(lon, lat, s = 150, c = con_idx, cmap = cm)
    cb = plt.colorbar()
    cb.set_label('Conflict index')
    

    # other setting
    plt.xlabel('lon. [deg.]', fontsize = 12)
    plt.ylabel('lat. [deg.]', fontsize = 12)
    plt.xticks([121.510,121.515,121.520,121.525,121.530,121.535,121.540],['121.510','121.515','121.520','121.525','121.530','121.535','121.540'])
    plt.yticks([25.01, 25.02, 25.03, 25.04, 25.05],['25.01', '25.02', '25.03', '25.04', '25.05'])
    plt.grid()
    plt.title('Conflict index distribution', fontsize = 14)
    plt.tight_layout()
    plt.show()
    
    
    return()


#initial data setting
first_raw_data = pd.read_csv('first_data.csv')
first_raw_information = pd.read_csv('first_information.csv', parse_dates = ['trav_time'])
second_raw_data = pd.read_csv('second_data.csv')
second_raw_information = pd.read_csv('second_information.csv', parse_dates = ['trav_time'])


# sort out data
# numbers of ways of each path
first_data = pd.DataFrame()
second_data = pd.DataFrame()
for i in range(np.size(first_raw_data,1)):
    a = first_raw_data['%s'%(i)].str.split(' ').str.get(0).dropna().astype(int)
    first_data = pd.concat([first_data, a], ignore_index=True, axis=1)
    a = second_raw_data['%s'%(i)].str.split(' ').str.get(0).dropna().astype(int)
    second_data = pd.concat([second_data, a], ignore_index=True, axis=1)

# other infor.s
distance_list1, time_list1, lat_list1, lon_list1, move_list1 = sort_information_data(first_raw_information)
distance_list2, time_list2, lat_list2, lon_list2, move_list2 = sort_information_data(second_raw_information)

#solve time format (to total seconds)
for i in range(len(time_list1)):
    time = datetime.datetime.strptime(time_list1[i], "0 days %H:%M:%S.000000000")
    time_list1[i] = int((time - datetime.datetime(1900, 1, 1)).total_seconds())/60 # [min.]
    time = datetime.datetime.strptime(time_list2[i], "0 days %H:%M:%S.000000000")
    time_list2[i] = int((time - datetime.datetime(1900, 1, 1)).total_seconds())/60 # [min.]


# calculating # of conflicts and # of steps   
step_num_list1, confilct_list1, conflict_index_list1, turn_list1 = way_to_conflict(first_data, move_list1)
step_num_list2, confilct_list2, conflict_index_list2, turn_list2 = way_to_conflict(second_data, move_list2)

#print result
# get info. from google maps
gmaps = googlemaps.Client(key=' ')
geocode_origin = gmaps.geocode('taiwan 10617')
geocode_destination = gmaps.geocode('taipei train station')
address_and_coor = [geocode_origin[0]["formatted_address"],\
                    geocode_destination[0]["formatted_address"],\
                    [geocode_origin[0]["geometry"]["location"]["lng"],\
                     geocode_origin[0]["geometry"]["location"]["lat"]],\
                    [geocode_destination[0]["geometry"]["location"]["lng"],\
                     geocode_destination[0]["geometry"]["location"]["lat"]]]

output_result(address_and_coor, distance_list1,\
              time_list1, conflict_index_list1, confilct_list1, turn_list1)
output_result(address_and_coor, distance_list2,\
              time_list2, conflict_index_list2, confilct_list2, turn_list2)

# plot
#comparison
# total conflict vs. total traveling time
plot_comparison_with_conflict(conflict_index_list1, time_list1, 'traveling time', '[min.]',[10,20],'lightcoral')
plot_comparison_with_conflict(conflict_index_list2, time_list2, 'traveling time', '[min.]',[10,20],'lightcoral')

# total conflict vs. total traveling ditance
plot_comparison_with_conflict(conflict_index_list1, distance_list1/1000, 'traveling distance', '[km]',[0, 10],'#FFE171')
plot_comparison_with_conflict(conflict_index_list2, distance_list2/1000, 'traveling distance', '[km]',[0, 10],'#FFE171')

# total conflict vs. total traveling rate
plot_comparison_with_conflict(conflict_index_list1, distance_list1/1000/time_list1*60, 'traveling rate', '[km/hr.]',[0, 50],'#00DBB7')
plot_comparison_with_conflict(conflict_index_list2, distance_list2/1000/time_list2*60, 'traveling rate', '[km/hr.]',[0, 50],'#00DBB7')

# comparison in conflict types (corssing, merging, diverging) in different paths
plot_conflict_type(confilct_list1)
plot_conflict_type(confilct_list2)

# comparison plot of conflict index / turning counts
plot_conflict_turning(conflict_index_list1, turn_list1)
plot_conflict_turning(conflict_index_list2, turn_list2)

# plots of confilct index distribution
plot_conflict_distribution(first_data,lat_list1, lon_list1)
plot_conflict_distribution(second_data,lat_list2, lon_list2)
