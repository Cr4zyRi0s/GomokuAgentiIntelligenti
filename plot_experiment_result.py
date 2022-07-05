import matplotlib.pyplot as plt
import json
import numpy as np
from ast import literal_eval
import os
global str

number_experiment = 3

newPath = "images/experiment-test" +str(number_experiment)
file = "\match_ai_sd2_bl_ai_sd2_wh_"

if not os.path.exists(newPath):
        os.makedirs(newPath+'/PlayImg')
        os.makedirs(newPath+'/TimeImg')

for j in range(1,6):
    name = "experiments\experiment-test"+str(number_experiment)+ file + str(j) + ".json"
   
    file_json = open(name)
    data = json.load(file_json)

    vec_x = np.array([])
    vec_y = np.array([])
    vec_color = np.array([])

    winner = data["winner"]

    moves = ()
    number_moves=0
    for move in data["moves"]:
        moves = moves +(move,) 
        number_moves = number_moves+1

    for k in range(number_moves):
        x = moves[k][0]
        vec_x = np.append(vec_x, x)
        y = moves[k][1]
        vec_y = np.append(vec_y, y)
        color = moves[k][2]
        vec_color= np.append(vec_color, color)

    annotations =np.arange(1,np.size(vec_x)+1)
    sizes = np.random.uniform(400, 400)
    color = np.array([]) 
    color_text = np.array([]) 

    plt.rcParams['axes.facecolor'] = '#EEDFCC'
    fig, ax = plt.subplots(1, figsize=(6, 5))
    for i in vec_color:
        if i== 1.0:
            color = np.append(color, "black")
        if i== 0.0: 
            color = np.append(color, "white")

    ax.scatter(vec_x, vec_y, s=sizes, c=color, vmin=0, vmax=100)
    ax.set(xlim=(-1, 15), xticks=np.arange(0, 15),
        ylim=(15,-1), yticks=np.arange(0, 15))
    ax.grid(b=True, which='major', color="white", linestyle='-', alpha=0.4)

    for i, label in enumerate(annotations):
        if color[i] == 'black':
            color_text = np.append(color_text, "white")
        else:
            color_text = np.append(color_text, "black")
        
        ax.annotate(label,
                            xy=(vec_x[i], vec_y[i]),
                            xytext=(vec_x[i]-0.25, vec_y[i]+0.2),  
                            color= color_text[i],
                            size = 11
                            )
        
    plt.suptitle("Gomoku Play Example", fontsize = 12)
    plt.title("Winner: "+winner +" player", fontsize=10)
    plt.xlabel("row")
    plt.ylabel("column")
    #plt.show()
    play_img = file+str(j)+'_PlayImg.png'
    fig.savefig(newPath+'/PlayImg'+ play_img)

    #Time Graph
    time_bl = np.array([])
    time_wh = np.array([])
    tup = ()
    count=0
    for move in data["move_data"]:
        temp = tuple(literal_eval(move))
        tup = tup +(temp,)    
        count = count+1

    fig = plt.figure(figsize=(6, 5))
    for i in range(count):
        if tup[i][2] == True:
            time_black = data["move_data"][str(tup[i])]["time"]
            time_bl = np.append(time_bl, time_black)
        else:
            time_white = data["move_data"][str(tup[i])]["time"]
            time_wh = np.append(time_wh, time_white)

    stop = np.size(time_wh)
    time_wh =time_wh[1:stop]
    ax_x_bl = np.arange(1, np.size(time_bl)+1)
    ax_x_wh = np.arange(1, np.size(time_wh)+1)

    plt.plot(ax_x_bl,time_bl, color='black', marker='o', linestyle='dashed',
        linewidth=2, markersize=8)
    '''
    for i in range(np.size(ax_x_bl)):
        plt.annotate(time_bl[i],
                            xy=(ax_x_bl[i], time_bl[i]),
                            xytext=(ax_x_bl[i]+0.1, time_bl[i]),  
                            color= "black",
                            size = 10
                            )
        
    '''
    
    plt.plot(ax_x_wh,time_wh, color='white', marker='o', linestyle='dashed',
        linewidth=2, markersize=8)
    '''
    for i in range(np.size(ax_x_wh)):
        plt.annotate(time_wh[i],
                            xy=(ax_x_wh[i], time_wh[i]),
                            xytext=(ax_x_wh[i]+0.07, time_wh[i]),  
                            color= "white",
                            size = 10
                            )
    '''
        
    plt.grid()
    plt.suptitle("Time taken by the player to place a stone", fontsize=12)
    plt.title("Winner: "+winner +" player", fontsize=10)
    plt.ylabel("Time")
    plt.xlabel("#move")

    #plt.show()

    img = file+str(j)+'_TimeImg.png'
    fig.savefig(newPath+'/TimeImg'+ img)

