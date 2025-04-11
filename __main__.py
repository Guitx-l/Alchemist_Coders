import util
import threading
from main_shooter import MainShooterClient, RotatedShooterClient
from main_goalkeeper import MainGoalKeeperClient, RotatedGoalKeeperClient
from main_goalkeeper import main as goal_main




if __name__ == '__main__':
    threading.Thread(target=lambda *_: util.start_client(MainShooterClient, RotatedShooterClient)).start()
    goal_main()
