import util
import threading
from shooter import MainShooterClient, RotatedShooterClient
from goalkeeper import main as goal_main



if __name__ == '__main__':
    threading.Thread(target=lambda *_: util.start_client(MainShooterClient, RotatedShooterClient)).start()
    goal_main()
