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

        # direction go to
        dB1 = [0,0,pV1[2]]
        dB2 = [0.4,0.4,pV2[2]]


        rbB1.goto((dB1), wait=False)
        rbB2.goto((dB2), wait=False)

        a = 0

        while not arrived:
            a += 1
            robot_1_arrived = rbB1.goto((dB1), wait=False)
            robot_2_arrived = rbB2.goto((dB2), wait=False)
            arrived = robot_1_arrived and robot_2_arrived
            if a == 1 :
                print(f"pB1 = {pB1} ; pB2 = {pB2} ; pV1 = {pV1} ; pV2 = {pV2} ; pBalle {pBalle}")

            elif arrived :
                print(f"pB1 = {pB1} ; pB2 = {pB2} ; pV1 = {pV1} ; pV2 = {pV2} ; pBalle {pBalle}")
                a = 0