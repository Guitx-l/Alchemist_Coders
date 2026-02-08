import rsk
import csv
import sys
import time
import numpy as np
import argparse
import pathlib
import matplotlib.pyplot as plt


POLLING_RATE = 60
STRAIGHTEN = 1
SAVE_GRAPH = False
REMOVE_PREVIOUS_DATA = False
DATA_FILE = pathlib.Path("./ball_graph.csv")


def valid_path(path_str: str) -> pathlib.Path:
    path = pathlib.Path(path_str)
    if not path.parent.exists():
        raise argparse.ArgumentTypeError(f"Le chemin {path_str} n'existe pas.")
    return path


def positive_int(value: str) -> int:
    """Check if the input is a positive integer greater than zero."""
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' n'est pas un entier avlide.")
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} n'est pas un entier positif valide (doit être > 0).")
    return ivalue


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Programme qui permet d'afficher ou de sauvegarder la position de la balle en fonction du temps")
    parser.add_argument('-m', '--mode', choices=['display', 'save'], help="Action réalisée par le script, soit 'display' pour afficher les infos de la balle, ou 'save' pour les sauvegarder")
    parser.add_argument('-s', '--straighten', type=positive_int, default=STRAIGHTEN, help="Degré de \"lissage\" lors de l'affichement des données")
    parser.add_argument('-S', '--save', type=valid_path, default=None, help="Si précisé, le graphique sera sauvegardé dans un fichier, sinon, le graphique ne sera pas sauvegardé")
    parser.add_argument('-p', '--polling_rate', type=positive_int, default=POLLING_RATE, help="Nombre de fois où les positions de balle sont sauvegardées par seconde")
    parser.add_argument('-d', '--data', type=valid_path, default=DATA_FILE, help="Chemin du fichier csv qui contient les données")
    parser.add_argument('-r', '--remove', action="store_true", default=REMOVE_PREVIOUS_DATA, help="Supprime toutes les données précédentes  du fichier lors de l'écriture")
    return parser


def save_data(csv_file_path: pathlib.Path, polling_rate: int, remove: bool = False) -> None:
    update_period = 1 / polling_rate
    
    if remove:
        open(csv_file_path, 'w').close() # Efface le contenu du fichier

    with rsk.Client() as client:
        with open(csv_file_path, 'a') as file:
            writer = csv.writer(file)
            while True:
                if client.ball is None or client.referee is None:
                    continue
                writer.writerow([
                    time.time(),
                    client.ball[0], 
                    client.ball[1],
                    1 if client.referee['game_is_running'] else 0
                ])
                time.sleep(update_period)
            

def display_data(straightening_level: int, output_path: pathlib.Path | None, csv_file_path: pathlib.Path) -> None:
    data = np.loadtxt(csv_file_path, delimiter=",")

    first_timestamp = data[0, 0]
    data[:, 0] -= first_timestamp
    print(f"Fréquence d'échantillonnage : {1/(data[1, 0]-data[0, 0])} Hz")

    timestamps = data[:, 0]
    ball_dx = np.diff(data[:, 1]) 
    ball_dy = np.diff(data[:, 2]) 
    game_is_running = data[:, 3]
    speed = np.sqrt(ball_dx**2 + ball_dy**2) / np.diff(timestamps)

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps[:-1], speed * 3.6, label="Vitesse totale de la balle")
    plt.xlabel("Temps (s)")
    plt.ylabel("Vitesse (km/h)")
    plt.title("Vitesse de la balle en fonction du temps")
    plt.grid(True)

    if output_path is not None:
        plt.savefig(output_path)
        print(f"Graphique sauvegardé dans {output_path}")
    else:
        plt.show()


def main() -> None:
    arguments = get_parser().parse_args(sys.argv[1:])
    print(arguments)
    if arguments.mode == "display":
        display_data(arguments.straighten, arguments.save, arguments.data)
    else:
        save_data(arguments.data, arguments.polling_rate, remove=arguments.remove)


if __name__ == "__main__":
    main()