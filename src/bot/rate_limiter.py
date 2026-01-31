import rsk
import time
from typing import Callable
from src.util.log import getLogger


def get_rate_limiter_dict(client_dict: dict = {}, client_update_func: Callable[[rsk.Client, str, int, dict], None] = lambda *x: None, refresh_rate: float = 60) -> dict:
    return {
        "logger": getLogger("rate_limiter"),
        "client_data": client_dict,
        "client_update": client_update_func,
        "update_period": 1 / refresh_rate,
        "last_timestamp": time.time(),
        "updated": False
    }


def rate_limiter_update(client: rsk.Client, team: str, number: int, data: dict):
    # constants
    client_data = data['client_data']
    client_update_func = data['client_update']

    if not data["updated"]:
        client_update_func(client, team, number, client_data)
        data["updated"] = True

    if (time.time() - data["last_timestamp"]) > data["update_period"]:
        data["last_timestamp"] = time.time()
        data["updated"] = False


if __name__ == "__main__":
    from src.util.init import start_client
    refersh_rate = 1
    start_client(rate_limiter_update, number=1, data_dict=get_rate_limiter_dict(refresh_rate=refersh_rate))