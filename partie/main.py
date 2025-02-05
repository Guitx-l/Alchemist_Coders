import threading
import rsk
from rsk import constants
from math import pi
import time
import main_shooter

threading.Thread(target=lambda *_: main_shooter.main("-t green -q --host rsk.simulateur.les-amicales.fr -k 01234".split(" "))).start()

color = "blue"
team = "teams"

if (color == "blue") :
    colorennemis = "green"
else :
    colorennemis = "blue"




with rsk.Client(host='rsk.simulateur.les-amicales.fr', key='43210') as client:
    try:
        robot1 = client.robots[color][1]
        robot2 = client.robots[color][2]
        robotennemis1 = client.robots[colorennemis][1]
        robotennemis2 = client.robots[colorennemis][2]
        
        refRobot1 = client.referee[team][color]["robots"]['1']
        refRobot2 = client.referee[team][color]["robots"]['2']
        """Il suffira de multiplier les x des robot et le l'emplacement des cages
        par x_pos pour obenir la position souhaité en fonction du coté de notre camp"""
        

        robot1.pose
    
    except Exception as e :
        print("erreur début with rsk.client... : ",e)
    arrived = True

    while True:
        ref = client.referee
        if(not ref["game_is_running"]):
            print(ref["game_is_running"])
            print(i)
            i += 1
            time.sleep(0.1)
            print("game isn't running")
        if(ref["game_is_running"]):

        pbut = constants.defense_area_width
            

            while True :
                try:
                    ref = client.referee
                    x_positive = client.referee[team][color]["x_positive"]
                
                    if (x_positive == True) :
                        x_pos = -1
                    else :
                        x_pos = 1

                    pbut = constants.defense_area_width

                except Exception as e :
                    print("erreur début while true : ",e)
                    