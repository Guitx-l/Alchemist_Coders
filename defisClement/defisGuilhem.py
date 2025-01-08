import rsk
from rsk import constants
from math import pi





#définir la couleur pour pouvoir obtenir la var c
rgb = int(input("indique ta couleur (0 pour Bleu et 1 pour Vert) : "))
if rgb == 0 :
    color = "blue"
    colorennemis = "green"
    
else :
    color = "green"
    colorennemis = "blue"


# ATENTION il faut definir la couleur et le coté
#c Definir la valeur par défault de la couleur
#    c = 1
#    c = -1


yCage = 0

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

    # une variable c définie le côté dans du terrain auquel notre équipe est attribué
    # la variable c sera positive ou négative en fonction du côté du terrain auquel est attribué notre équipe
    # fonction try permet de ne pas avoir de problème si le le game controleur ne repond pas
    try :
        #d détermine le coté du terrain
        c = client.referee["Alchemist_Coder"][color]["x_positive"]

    except :
        c = int(input("indique le côté de ton equipe (-1 côté gauche & 1 côté droit) : "))
        # Il n'y a pas besoin de ré-attribuer c car il n'a pas été mofifié





    # raccourcis commande robot
    # rbp1 robot piloté n°1 (que je pilote) 
    # rbe1 robot ennemis n°1 
    rbp1 = client.robots[color][1]
    rbp2 = client.robots[color][2]
    rbe1 = client.robots[colorennemis][1]
    rbe2 = client.robots[colorennemis][2]
    
    arrived = False
    
    while True :
        
        # position p -> piloté  e -> ennemis
        pp1 = rbp1.pose
        pp2 = rbp2.pose
        pe1 = rbe1.pose
        pe2 = rbe2.pose
        pBalle = client.ball

        """afin determiner contre quel robot le goal doit se défendre,
        il est nécéssaire de definir une fonction pour déterminer quel robot est le plus à même de marque un but.
        
        Si sur l'ordre des x, un robot se trouve devant la balle il n'est pas dangereux, sauf s'il se rapproche trop vite ou est à une distance trop courte
        si les deux robot se trouvent à des distance trop éloignées ou devant la balle les robot ne sont pas dangereux
        
        robot1 -> dangereux         : protection contre rb1
        robot2 -> dangereux         : protection contre rb1
        aucun robot -> dangereux    : passe en mode attaquant 
        en transaction              : change de robot lorsqu'il se font la passe 
        les 2 robots potentiellement dangereux :
        le defenseur se place de manière à pouvoir se positionner rapidement en cas d'attaque de l'un des 2 robot ennemis"""




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