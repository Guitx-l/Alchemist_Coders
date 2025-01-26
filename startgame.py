import rsk


color = "blue"
team = "teams"

if (color == "blue") :
    colorennemis = "green"
else :
    colorennemis = "blue"






with rsk.Client(host='127.0.0.1', key='') as client:
    try:
        robot1 = client.robots[color][1]
        robot2 = client.robots[color][2]
        robotennemis1 = client.robots[colorennemis][1]
        robotennemis2 = client.robots[colorennemis][2]
        ref = client.referee[team][color]
        refRobot1 = client.referee[team][color]["robots"]['1']
        refRobot2 = client.referee[team][color]["robots"]['2']
        """Il suffira de multiplier les x des robot et le l'emplacement des cages
        par x_pos pour obenir la position souhaité en fonction du coté de notre camp"""
        x_positive = ref["x_positive"]
        if (x_positive == True) :
            x_pos = -1
        else :
            x_pos = 1

        robot1.pose
    
    except Exception as e :
        print("erreur début with rsk.client... : ",e)

    rb1 = refRobot1["preemption_reasons"]
    rb = refRobot2["preemption_reasons"]
    print(rb1)
    print(rb)
    print("")

    while True :

        try:
            if(refRobot1["preempted"] == True or refRobot2["preempted"] == True) :
                rb1 = refRobot1["preemption_reasons"]
                rb = refRobot2["preemption_reasons"]
                if(rb1 != refRobot1["preemption_reasons"] or rb != refRobot2["preemption_reasons"]):
                    print(rb1)
                    print(rb)
                    print("")
        except Exception as e :
            print("erreur début while true : ",e)
