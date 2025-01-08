import rsk
from rsk import constants
from math import pi



def cages(pe1,pBalle):
    global yCage
    if (pe1[0] - pBalle[0]) == 0 :
        a = 0
    else :
        #ATTENTION equipe bleu donc yCage = - yCage voir le - du a
        # Ya-Yb/Xa-Xb
        a = - (pe1[1] - pBalle[1]) / (pe1[0] - pBalle[0])

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

    # raccourcis commande robot
    rbp1 = client.blue1
    rbp2 = client.blue2
    rbe1 = client.green1
    rbe2 = client.green2

    arrived = False
    


    while True :
        
        # position p -> piloté  e -> ennemis
        pp1 = rbp1.pose
        pp2 = rbp2.pose
        pe1 = rbe1.pose
        pe2 = rbe2.pose
        pBalle = client.ball

        # postition que le défenceur doit prendre pour se positionner au niveaux des cages
        # ATTENTION pbut = - constants.defense_area_width car constants.defense_area_width 
        pbut = - constants.defense_area_width



        # postition que le défenceur doit prendre pour se positionner au niveaux des cages
        """ ATTENTION à la couleur des joueurs
        pbut = - constants.defense_area_width car constants.defense_area_width 
        """
        pbut = - constants.defense_area_width

        cages(pe1,pBalle)

        # direction go to
        dp1 = [0,0.61,pe1[2] + pi]
        dp2 = [pbut,yCage,0]





        rbp1.goto((dp1), wait=False)
        rbp2.goto((dp2), wait=False)

        i = 0

        while not arrived:
            i += 1
            robot_1_arrived = rbp1.goto((dp1), wait=False)
            robot_2_arrived = rbp2.goto((dp2), wait=False)
            print(yCage)
            arrived = robot_1_arrived and robot_2_arrived
            if i == 1 :
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
                i = 0