import rsk
import time



with rsk.Client(host='127.0.0.1', key='') as client:
    client.blue1.leds(0, 255, 0)
    client.blue1.leds(0, 255, 0)
    try:
        color = "blue"
        team = "teams"
        robot1 = client.robots[color][1]
        robot2 = client.robots[color][2]
        ref = client.referee[team][color]
        refRobot1 = client.referee[team][color]["robots"]['1']
        refRobot2 = client.referee[team][color]["robots"]['2']
        x_pos = ref["x_positive"]
        print(x_pos)


        print("Robot 1")
        #client referee robot1
        penalized1 =  refRobot1["penalized"]
        print(penalized)

        penalized_reason1 =  refRobot1["penalized_reason"]
        print(penalized_reason)

        penalized_remaining1 =  refRobot1["penalized_remaining"]
        print(penalized_remaining)

        preempted1 =  refRobot1["preempted"]
        print(preempted)

        preemption_reasons1 =  refRobot1["preemption_reasons"]
        print(preemption_reasons)


        #client referee robot 2
        print("Robot 2")
        penalized2 =  refRobot2["penalized"]
        print(penalized)

        penalized_reason2 =  refRobot2["penalized_reason"]
        print(penalized_reason)

        penalized_remaining2 =  refRobot2["penalized_remaining"]
        print(penalized_remaining)

        preempted2 =  refRobot2["preempted"]
        print(preempted)

        preemption_reasons2 =  refRobot2["preemption_reasons"]
        print(preemption_reasons)

     except Exception as e :
        print(e)

    time.sleep(1)