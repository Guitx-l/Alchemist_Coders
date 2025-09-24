import threading
from util.init import start_client
from multi_client import MultiClient



if __name__ == '__main__':
    threading.Thread(target=start_client, args=(
        (lambda client, team: MultiClient(client, team, 1)),
    )).start()
    start_client(
        (lambda client, team: MultiClient(client, team, 2)),
    )

