import rsk
from rsk import constants
from math import pi

with rsk.Client() as client:

    while True :
        rbB1 = client.blue1
        rbB2 = client.blue2
        rbV1 = client.green1
        rbV2 = client.green2

        pB1 = rbB1.pose
        pB2 = rbB2.pose
        pV1 = rbV1.pose
        pV2 = rbV2.pose
        pBalle = client.ball

        
        rbB1.goto((0,0,pi), wait=False)
        print(f"pB1 = {round(pB1[0],2), round(pB1[1],2), round(pB1[2],2)} ;") 
        print(f"pB2 = {round(pB2[0],2), round(pB2[1],2), round(pB2[2],2)} ;")
        print(f"pV1 = {round(pV1[0],2), round(pV1[1],2), round(pV1[2],2)} ;")
        print(f"pV2 = {round(pV2[0],2), round(pV2[1],2), round(pV2[2],2)} ;")
        print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
        