import rsk

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



