import rsk
import time

with rsk.Client(host='127.0.0.1', key='1') as client:
    try :
        c = client.referee["Alchemist_Coder"][color]["x_positive"]
        print(c)
    except :
        print("no color detected")

while True :
    time.sleep(1000)