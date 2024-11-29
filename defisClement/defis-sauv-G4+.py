import rsk
from rsk import constants
from math import pi





#définir la couleur pour pouvoir obtenir la var c
rgb = bool(input(print("indique ta couleur (0 pour Bleu et 1 pour Vert) : ")))
if rgb == 0 :
    color = 'Blue'
    #c Definir la valeur par défault de la couleur
    c = 1
else :
    color = 'Green'
    c = -1

# ATENTION il faut definir la couleur et le coté





yCage = 0

def cages(pV1,pBalle):
    global yCage
    if (pV1[0] - pBalle[0]) == 0 :
        a = 0
    else :
        #ATTENTION equipe bleu donc yCage = - yCage voir le - du a
        # Ya-Yb/Xa-Xb
        a = - (pV1[1] - pBalle[1]) / (pV1[0] - pBalle[0])

    #ATTENTION equipe bleu donc yCage = - yCage
    # b = yballe - a * xballe
    yCage = pBalle[1] - (a * pBalle[0])

    """ La taille des cages et de 60cm soit y [+0.30 ; -0.30].
        Le robot fait 7 cm re rayon réel. Avec une marge, on dira
        qu'il fait 6cm : 30 - 6 = 24
        donc le robot bougera ds l'intervalle y [+0.24 ; -0.24]"""

    if yCage > 0.24 :
        yCage = 0.24
    elif yCage < -0.24 :
        yCage = -0.24

    return(yCage)






with rsk.Client() as client:

    # une variable c définie le côté dans du terrain auquel notre équipe est attribué
    # la variable c sera positive ou négative en fonction du côté du terrain auquel est attribué notre équipe
    # fonction try permet de ne pas avoir de problème si le le game controleur ne repond pas
    try :
        c = client.referee["Alchemist_Coder"][color]["x_positive"]

    except :
        print(f"Couleur '{color}' par défault")
        # Il n'y à pas besoin de réattribuer c car il n'a pas été mofifié







    # raccourcis commande robot
    rbB1 = client.blue1
    rbB2 = client.blue2
    rbV1 = client.green1
    rbV2 = client.green2
    
    arrived = False
    
    while True :
        
        # position
        pB1 = rbB1.pose
        pB2 = rbB2.pose
        pV1 = rbV1.pose
        pV2 = rbV2.pose
        pBalle = client.ball
        # postition que le défenceur doit prendre pour se positionner au niveaux des cages
        """ ATTENTION à la couleur des joueurs
        pbut = - constants.defense_area_width car constants.defense_area_width 
        """
        pbut = - constants.defense_area_width

        cages(pV1,pBalle)

        # direction go to
        dB1 = [0,0.61,pV1[2] + pi]
        dB2 = [pbut,yCage,0]


        rbB1.goto((dB1), wait=False)
        rbB2.goto((dB2), wait=False)

        i = 0

        while not arrived:
            i += 1
            robot_1_arrived = rbB1.goto((dB1), wait=False)
            robot_2_arrived = rbB2.goto((dB2), wait=False)
            print(yCage)
            arrived = robot_1_arrived and robot_2_arrived
            if i == 1 :
                print(f"pB1 = {round(pB1[0],2), round(pB1[1],2), round(pB1[2],2)} ;") 
                print(f"pB2 = {round(pB2[0],2), round(pB2[1],2), round(pB2[2],2)} ;")
                print(f"pV1 = {round(pV1[0],2), round(pV1[1],2), round(pV1[2],2)} ;")
                print(f"pV2 = {round(pV2[0],2), round(pV2[1],2), round(pV2[2],2)} ;")
                print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
                
            elif arrived :
                print(f"pB1 = {round(pB1[0],2), round(pB1[1],2), round(pB1[2],2)} ;") 
                print(f"pB2 = {round(pB2[0],2), round(pB2[1],2), round(pB2[2],2)} ;")
                print(f"pV1 = {round(pV1[0],2), round(pV1[1],2), round(pV1[2],2)} ;")
                print(f"pV2 = {round(pV2[0],2), round(pV2[1],2), round(pV2[2],2)} ;")
                print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
                i = 0