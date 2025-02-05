import rsk
from rsk import constants
from math import pi
import time

color = "blue"
team = "teams"
cote = 1 #definir le cote du terrain avec 0 ou 1
pbut = constants.defense_area_width

i = 0





if (color == "blue") :
    colorennemis = "green"
else :
    colorennemis = "blue"

#
#
#   cote == 1
#
#
def cages1(pBalle):
    dB2 = []
    yCage = pBalle[1]

    """ La taille des cages et de 60cm soit y [+0.30 ; -0.30].
        Le robot fait 7 cm re rayon réel. Avec une marge, on dira
        qu'il fait 6cm : 30 - 6 = 24
        donc le robot bougera ds l'intervalle y [+0.24 ; -0.24]"""
    if yCage > 0.25 :
        yCage = 0.24
    elif yCage < -0.25 :
        yCage = -0.24







    if (-0.2<robot2.pose[0] - pBalle[0] < 0.2) :
        # goto shoot ball
        dB2 = [(pBalle[0] - 0.1),pBalle[1],0] #if x_pos == 1 else pi]
    else :
        dB2 = [pbut,yCage,0]# if x_pos == 1 else pi]

    if (dB2[0]> )
    #dB2[0] = dB2[0] * (-1)

    if (dB2[2] > pi):
        dB2[2] = dB2[2] - pi
    return(dB2)

"""faire que le robot se déplace en fonction de l'orientation du robot attaquant"""
    
"""creer 2 programes en fonction de si xpos est à 1 ou -1"""



def defenseur1():

    try:
        dB2 =  cages(pBalle)
        #print(dB2)
        
        if(not refRobot2["penalized"] and not refRobot2["preempted"]) :
            #print("if rbt2 fonctionne")
            robot2.goto((dB2), wait=False)
            arrived = False
            #if x_pos == -1:
            if pBalle[0] > constants.field_length/2 - constants.defense_area_length:
                robot2.kick()
            #else:
            #    if pBalle[0] < -constants.field_length/2 + rsk.constants.defense_area_length:
            #        robot2.kick()
        else :
            print(refRobot1["penalized"], " and ", refRobot1["preemption_reasons"])
        arrived = False


        while not arrived :
            robot_2_arrived = robot2.goto((dB2), wait=False)
            arrived = robot_2_arrived
            if arrived :
                #print(f"pp1 = {round(pp1[0],2), round(pp1[1],2), round(pp1[2],2)} ;") 
                #print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
                arrived = True
    except rsk.client.ClientError as e:
        pass



#
#
#
#
#
#
#
#

def lancement():
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
                
        except Exception as e :
            print("erreur début with rsk.client... : ",e)
        arrived = True





        
        while True :

            try:
                # Position + orientation (x [m], y [m], theta [rad])
                # position p -> piloté  e -> ennemis
                pp1 = robot1.pose
                pp2 = robot2.pose
                pe1 = robotennemis1.pose
                pe2 = robotennemis2.pose
                pBalle = client.ball
                # postition que le défenceur doit prendre pour se positionner au niveaux des cages
                # ATTENTION pbut = - constants.defense_area_width car constants.defense_area_width
            except Exception as e :
                print("erreur début while true : ",e)

            
            cages[cote](pBalle)
            defenseur[cote]()



lancement()