import sys
import threading
sys.path.append(".")
from src.util.init import start_client
from src.bot.multi_client import MultiClient

def get_bot1(client, team):
    return MultiClient(client, team, 1)

def get_bot2(client, team):
    return MultiClient(client, team, 2)

if __name__ == '__main__':
    threading.Thread(target=start_client, args=[get_bot1]).start()
    start_client(get_bot2)

