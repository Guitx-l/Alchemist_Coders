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

        except Exception as e :
            print(e)