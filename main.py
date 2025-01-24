import threading
import rsk
from rsk import constants
from math import pi
import time
import main_shooter

threading.Thread(main_shooter.main())

color = "blue"
team = "teams"

if (color == "blue") :
    colorennemis = "green"
else :
    colorennemis = "blue"

pbut = constants.defense_area_width


i = 0


def defenseur():

    cages(pBalle)
    dB2 = [pbut,yCage,0]


        
    if(not refRobot2["penalized"] and not refRobot2["preempted"]) :
        print("if rbt2 fonctionne")
        robot2.goto((dB2), wait=False)
        arrived = False
    else :
        print(refRobot1["penalized"], " and ", refRobot1["preempted"])
    


    while not arrived :
        robot_2_arrived = robot2.goto((dB2), wait=False)
        arrived = robot_2_arrived
        if arrived :
            print(f"pp1 = {round(pp1[0],2), round(pp1[1],2), round(pp1[2],2)} ;") 
            print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
            robot1.kick()
            arrived = True





def cages(pBalle):
    global yCage
    yCage = pBalle[1]

    """ La taille des cages et de 60cm soit y [+0.30 ; -0.30].
        Le robot fait 7 cm re rayon réel. Avec une marge, on dira
        qu'il fait 6cm : 30 - 6 = 24
        donc le robot bougera ds l'intervalle y [+0.24 ; -0.24]"""
    if yCage > 0.25 :
        yCage = 0.24
    elif yCage < -0.25 :
        yCage = -0.24

    

    return(yCage)