import util
import threading
from multi_client import MainMultiClient, RotatedMultiClient



if __name__ == '__main__':
    threading.Thread(target=util.start_client, args=(
        (lambda client, team: MainMultiClient(client, team, 1)),
        (lambda client, team: RotatedMultiClient(client, team, 1))
    )).start()
    util.start_client(
        (lambda client, team: MainMultiClient(client, team, 2)),
        (lambda client, team: RotatedMultiClient(client, team, 2))
    )
