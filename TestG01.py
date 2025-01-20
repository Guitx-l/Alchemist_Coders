import rsk
from rsk import constants

with rsk.Client(host='127.0.0.1', key='') as client:
    client.green1

x1 = 0
y1 = 0
orient1 = 0
xb = 0
yb = 0

def loc(x1,x2,y1,y2,orient1,orient2,client.green1.pose,client.green2.pose) :
    x1 = client.green1.pose[0]
    y1 = client.green1.pose[1]
    orient1 = client.green1.pose[2]
    xb = client.ball[0]
    yb = client.ball[1]
    return(x1,x2,y1,y2,orient1,orient2,xb,yb)

while True :
    loc(x1,x2,y1,y2,orient1,orient2,xb,yb)
    arrived = False
    while not arrived:
        robot_1_arrived = client.green1.goto((0.2, 0.3, 0.), wait=False)
        robot_2_arrived = client.green2.goto((0.2, -0.3, 0.), wait=False)
        arrived = robot_1_arrived and robot_2_arrived
        robot.goto((0.2, 0.5, 1.2))


