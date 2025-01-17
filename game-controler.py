import rsk
import time



with rsk.Client(host='127.0.0.1', key='1') as client:

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
        penalized =  refRobot1["penalized"]
        print(penalized)

        penalized_reason =  refRobot1["penalized_reason"]
        print(penalized_reason)

        penalized_remaining =  refRobot1["penalized_remaining"]
        print(penalized_remaining)

        preempted =  refRobot1["preempted"]
        print(preempted)

        preemption_reasons =  refRobot1["preemption_reasons"]
        print(preemption_reasons)


        #client referee robot 2
        print("Robot 2")
        penalized =  refRobot2["penalized"]
        print(penalized)

        penalized_reason =  refRobot2["penalized_reason"]
        print(penalized_reason)

        penalized_remaining =  refRobot2["penalized_remaining"]
        print(penalized_remaining)

        preempted =  refRobot2["preempted"]
        print(preempted)

        preemption_reasons =  refRobot2["preemption_reasons"]
        print(preemption_reasons)

     except Exception as e :
        print(e)

    time.sleep(1)