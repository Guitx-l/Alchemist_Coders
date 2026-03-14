import sys
import threading
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.util.init import start_client
from src.bot.role_manager import get_role_manager_dict, role_manager_update

if __name__ == '__main__':
    threading.Thread(target=start_client, args=[role_manager_update, 1, get_role_manager_dict()]).start()
    start_client(role_manager_update, number=2, data_dict=get_role_manager_dict())
