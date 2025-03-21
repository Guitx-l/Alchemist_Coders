import rsk
import util
import main_shooter
import threading


def simple_goalkeeper(team: str, rotated: bool = False):
    with rsk.Client() as client:
        goalkeeper: rsk.client.ClientRobot = client.robots[team][2]
        while True:
            if rotated:
                if util.is_inside_right_zone(client.ball):
                    goalkeeper.goto((*client.ball, 3.14))
            elif util.is_inside_left_zone(client.ball):
                goalkeeper.goto((*client.ball, 0))

def main(args: list[str] | None = None) -> None:
    threading.Thread(target=lambda *_: main_shooter.main()).start()
    main_shooter.main("-t green -r".split())
    print("idk")

if __name__ == '__main__':
    main()
