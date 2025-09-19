import threading
import logging
from util import start_client
from multi_client import MultiClient



if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] [%(name)s] (%(asctime)s) - %(message)s',
        datefmt='%H:%M:%S'
    )

    threading.Thread(target=start_client, args=(
        (lambda client, team: MultiClient(client, team, 1)),
    )).start()
    start_client(
        (lambda client, team: MultiClient(client, team, 2)),
    )

