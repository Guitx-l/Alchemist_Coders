import threading
from util import start_client
from multi_client import BaseMultiClient


if __name__ == '__main__':
    threading.Thread(target=start_client, args=(
        (lambda client, team: BaseMultiClient(client, team, 1)),
    )).start()
    start_client(
        (lambda client, team: BaseMultiClient(client, team, 2)),
    )

