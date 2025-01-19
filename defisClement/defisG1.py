import rsk

while True :
    
    with rsk.Client() as client: 
        rbB1 = client.blue1

        while True:
            rbB1.goto((0,0,0), wait=False)