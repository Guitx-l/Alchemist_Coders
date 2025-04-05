import rsk
import util
import sys
import threading
from typing import Type, Literal
from main_goalkeeper import MainGoalKeeperClient, RotatedGoalKeeperClient
from main_shooter import MainShooterClient, RotatedShooterClient

from util import IClient

def start_client(MainClass: Type[IClient], RotatedClass: Type[IClient], args: list[str] | None = None):
    arguments = util.get_parser("Script that runs the shooter (adapted to halftime change)").parse_args(sys.argv[1::] if args is None else args)
    logger = util.Logger(__name__, True)
    logger.info(f"args: {arguments}")
    team = arguments.team
    rotated: bool = arguments.rotated

    with rsk.Client(host=arguments.host, key=arguments.key) as c:  # tkt c un bordel mais touche pas ca marche nickel
        shooter_client = MainClass(c, team) if not rotated else RotatedClass(c, team)
        halftime = True
        pause = True
        shooter_client.startup()
        while True:
            if c.referee['halftime_is_running']:
                if halftime:
                    shooter_client = RotatedClass(c, team) if not rotated else MainClass(c, team)
                    logger.info(f"halftime, changing into {shooter_client.__class__}")
                    rotated = not rotated
                    halftime = False
            else:
                halftime = True
            if c.referee["game_paused"]:
                if pause:
                    shooter_client.on_pause()
                    pause = False
            else:
                pause = True

            try:
                shooter_client.update()
            except rsk.client.ClientError as e:
                if arguments.verbose:
                    shooter_client.logger.warn(e)


def main():
    threading.Thread(target=lambda *_: start_client(MainShooterClient, RotatedShooterClient, sys.argv[1::])).start()
    start_client(MainGoalKeeperClient, RotatedGoalKeeperClient, sys.argv[1::])

if __name__ == '__main__':
    main()