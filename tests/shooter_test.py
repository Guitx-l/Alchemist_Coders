import main_shooter
import threading


def main(args: list[str] | None = None) -> None:
    threading.Thread(target=lambda *_: main_shooter.main()).start()
    main_shooter.main("-t green -r".split())
