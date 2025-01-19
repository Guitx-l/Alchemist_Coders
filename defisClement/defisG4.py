import rsk
from rsk import constants
from math import pi

with rsk.Client() as client:
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
        # ATTENTION pbut = - constants.defense_area_width car constants.defense_area_width 
        pbut = - constants.defense_area_width

        # direction go to
        dB1 = [0,0,pV1[2]]
        dB2 = [pbut,pBalle[1],0]


        rbB1.goto((dB1), wait=False)
        rbB2.goto((dB2), wait=False)

        a = 0

        while not arrived:
            a += 1
            robot_1_arrived = rbB1.goto((dB1), wait=False)
            robot_2_arrived = rbB2.goto((dB2), wait=False)
            arrived = robot_1_arrived and robot_2_arrived
            if a == 1 :
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
                a = 0