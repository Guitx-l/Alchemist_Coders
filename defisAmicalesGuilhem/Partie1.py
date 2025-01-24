import rsk
import time


color = "blue"
team = "teams"
    



with rsk.Client(host='127.0.0.1', key='') as client:
    
    try:
        robot1 = client.robots[color][1]
        robot2 = client.robots[color][2]
        ref = client.referee[team][color]
        x_pos = ref["x_positive"]
        print(x_pos)
        consGoal = rsk.constants.goal_width
        print("consGoal = ",consGoal)

    except Exception as e :
        print("erreur",e)



    while True :
        time.sleep(2)
        try :
            # Position + orientation (x [m], y [m], theta [rad])     
            prb1 = robot1.pose
            prb2 = robot2.pose
            print(prb1," && ",prb2)

            # Ball's position (x [m], y [m])
            client.ball

            x_pos = ref["x_positive"]
            print(x_pos)

        except Exception as e :
            print(e)

        
        # direction go to
        dB1 = [client.ball[0]-0.1*x_pos,client.ball[1],pe1[2]/2 + pi]
        dB1[1] = dB1[1] * x_pos
        dB2 = [pbut,yCage,0]

        print("if arrivée validée")
        if(refRobot1["penalized"] == False and refRobot1["preempted"] == False) :
            print("if rbt1 fonctionne")
            robot1.goto((dB1), wait=False)
            arrived = False
        
        else :
            print(refRobot1["penalized"], " and ", refRobot1["preempted"])
            
        if(refRobot2["penalized"] == False and refRobot2["preempted"] == False) :
            print("if rbt2 fonctionne")
            robot2.goto((dB2), wait=False)
            arrived = False
        


        while not arrived :
            robot_1_arrived = robot1.goto((dB1), wait=False)
            robot_2_arrived = robot2.goto((dB2), wait=False)
            arrived = robot_1_arrived and robot_2_arrived
            if arrived :
                print(f"pp1 = {round(pp1[0],2), round(pp1[1],2), round(pp1[2],2)} ;") 
                print(f"pp2 = {round(pp2[0],2), round(pp2[1],2), round(pp2[2],2)} ;")
                print(f"pe1 = {round(pe1[0],2), round(pe1[1],2), round(pe1[2],2)} ;")
                print(f"pe2 = {round(pe2[0],2), round(pe2[1],2), round(pe2[2],2)} ;")
                print(f"pBalle {round(pBalle[0],2), round(pBalle[1],2)} ;\n")
                robot1.kick()
                arrived = True