import util
import sys
import threading
from main_goalkeeper import MainGoalKeeperClient, RotatedGoalKeeperClient
from main_shooter import MainShooterClient, RotatedShooterClient


if __name__ == '__main__':
    threading.Thread(target=lambda *_: util.start_client(MainShooterClient, RotatedShooterClient)).start()
    util.start_client(MainGoalKeeperClient, RotatedGoalKeeperClient)
