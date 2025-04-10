import util
import threading
from main_shooter import MainShooterClient, RotatedShooterClient
from main_goalkeeper import MainGoalKeeperClient, RotatedGoalKeeperClient




if __name__ == '__main__':
    threading.Thread(target=lambda *_: util.start_client(MainShooterClient, RotatedShooterClient)).start()
    util.start_client(MainGoalKeeperClient, RotatedGoalKeeperClient)
