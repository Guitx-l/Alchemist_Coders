import threading
from util import start_client
from multi_client import MainMultiClient, RotatedMultiClient



if __name__ == '__main__':
    threading.Thread(target=start_client, args=(
        (lambda client, team: MainMultiClient(client, team, 1)),
        (lambda client, team: RotatedMultiClient(client, team, 1))
    )).start()
    start_client(
        (lambda client, team: MainMultiClient(client, team, 2)),
        (lambda client, team: RotatedMultiClient(client, team, 2))
    )
