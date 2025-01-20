import rsk
from rsk import constants
from math import pi

color = "blue"
team = "teams"

if (color == "blue") :
    colorennemis = "green"
else :
    colorennemis = "blue"




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






with rsk.Client(host='127.0.0.1', key='') as client:
    try:
        robot1 = client.robots[color][1]
        robot2 = client.robots[color][2]
        robotennemis1 = client.robots[colorennemis][1]
        robotennemis2 = client.robots[colorennemis][2]
        ref = client.referee[team][color]
        refRobot1 = client.referee[team][color]["robots"]['1']
        refRobot2 = client.referee[team][color]["robots"]['2']
        """Il suffira de multiplier les x des robot et le l'emplacement des cages
        par x_pos pour obenir la position souhaité en fonction du coté de notre camp"""
        x_positive = ref["x_positive"]
        print(x_positive)
        if (x_positive == True) :
            x_pos = 1
        else :
            x_pos = -1

        arrived = False
    
    except Exception as e :
        print(e)

    
    

    while True :
        # Position + orientation (x [m], y [m], theta [rad])
        # position p -> piloté  e -> ennemis
        pp1 = robot1.pose
        pp2 = robot2.pose
        pe1 = robotennemis1.pose
        pe2 = robotennemis2.pose
        pBalle = client.ball
        # postition que le défenceur doit prendre pour se positionner au niveaux des cages
        # ATTENTION pbut = - constants.defense_area_width car constants.defense_area_width 
        pbut = - constants.defense_area_width

        cages(pBalle)

        # direction go to
        dB1 = [-0.2,0,pe2[2] + pi]
        dB2 = [pbut,yCage,0]


        robot2.goto((dB2), wait=False)
        robot1.goto((dB1), wait=False)


        while not arrived :
            robot_1_arrived = robot1.goto((dB1), wait=False)
            robot_2_arrived = robot2.goto((dB2), wait=False)
            arrived = robot_1_arrived and robot_2_arrived
            if not arrived :
                print(f"pp1 = {round(pp1[0],2), round(pp1[1],2), round(pp1[2],2)} ;") 
                print(f"pp2 = {round(pp2[0],2), round(pp2[1],2), round(pp2[2],2)} ;")
                print(f"pe1 = {round(pe1[0],2), round(pe1[1],2), round(pe1[2],2)} ;")
                print(f"pe2 = {round(pe2[0],2), round(pe2[1],2), round(pe2[2],2)} ;")
                print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
                
            elif arrived :
                print(f"pp1 = {round(pp1[0],2), round(pp1[1],2), round(pp1[2],2)} ;") 
                print(f"pp2 = {round(pp2[0],2), round(pp2[1],2), round(pp2[2],2)} ;")
                print(f"pe1 = {round(pe1[0],2), round(pe1[1],2), round(pe1[2],2)} ;")
                print(f"pe2 = {round(pe2[0],2), round(pe2[1],2), round(pe2[2],2)} ;")
                print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
