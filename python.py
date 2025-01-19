import rsk
from rsk import constants



with rsk.Client() as client:
    client.green1.kick()

with rsk.Client(host='127.0.0.1', key='') as client:
    client.robots['green'][1].kick()

# Shortcuts to access a robot
client.green1
client.green2
client.blue1
client.blue2

# Full syntax allowing dynamic access
client.robots['green'][1]
client.robots['green'][2]
client.robots['blue'][1]
client.robots['blue'][2]

# Robot position (x [m], y [m]):
client.green1.position
# Robot orientation (theta [rad]):
client.green1.orientation
# Position + orientation (x [m], y [m], theta [rad])
client.green1.pose
# Ball's position (x [m], y [m])
client.ball

# Field length (x axis)
constants.field_length
# Field width (y axis)
constants.field_width

# Goal width
constants.goal_width

# Side of the (green) border we should be able to see around the field
constants.border_size



# Kicks, takes an optional power parameter between 0 and 1
robot.kick()

# Controls the robots in its own frame, arguments are x speed [m/s],
# y speed [m/s] and rotation speed [rad/s]

# Go forward, 0.25 m/s
robot.control(0.25, 0., 0.)

# Rotates 30 deg/s counter-clockwise
robot.control(0., 0., math.radians(30))




try:
    robot.kick()
    robot.control(0.1, 0, 0)
except rsk.ClientError:
    print('Error during a command!')




# Sending a robot to x=0.2m, y=0.5m, theta=1.2 rad
robot.goto((0.2, 0.5, 1.2))



# Placing two robots, the loop will block until both robots are placed
arrived = False
while not arrived:
    robot_1_arrived = client.green1.goto((0.2, 0.3, 0.), wait=False)
    robot_2_arrived = client.green2.goto((0.2, -0.3, 0.), wait=False)
    arrived = robot_1_arrived and robot_2_arrived




def print_the_ball(client, dt):
    print(client.ball)

# This will print the ball everytime a new information is obtained from the client
client.on_update = print_the_ball
