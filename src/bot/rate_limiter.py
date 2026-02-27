import rsk
import time
from typing import Callable
from src.util.log import getLogger


def get_rate_limiter_dict(sub_client_dict: dict = {}, sub_client_update_func: Callable[[rsk.Client, str, int, dict], None] = lambda *x: None, refresh_rate: float = 60) -> dict:
    return {
        "logger": getLogger("rate_limiter"),
        "client_data": sub_client_dict,
        "client_update": sub_client_update_func,
        "update_period": 1 / refresh_rate,
        "last_timestamp": time.time(),
        "client_updated": False
    }


def rate_limiter_update(client: rsk.Client, team: str, number: int, data: dict):
    client_data = data['client_data']
    client_update_func = data['client_update']

    if not data["client_updated"]:
        client_update_func(client, team, number, client_data)
        data["client_updated"] = True

    if (time.time() - data["last_timestamp"]) > data["update_period"]:
        data["last_timestamp"] = time.time()
        data["client_updated"] = False


if __name__ == "__main__":
    from src.util.init import start_client
    refersh_rate = 1
    start_client(rate_limiter_update, number=1, data_dict=get_rate_limiter_dict(refresh_rate=refersh_rate))