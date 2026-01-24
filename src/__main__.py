import sys
import threading
sys.path.append(".")
from src.util.init import start_client
from src.bot.multi_client import get_multi_bot_dict, multi_update

if __name__ == '__main__':
    threading.Thread(target=start_client, args=[multi_update, 1, get_multi_bot_dict()]).start()
    start_client(multi_update, number=2, data_dict=get_multi_bot_dict())
