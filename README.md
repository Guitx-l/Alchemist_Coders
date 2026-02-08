<h1 style="text-align: center" align="center">Alchemist Coders</h1>

<p style="text-align: center; font-style: italic" align="center">L'esprit du jeu, l'alchimie du code et de la stratégie</p>

<p style="text-align: center" align="center">
<img src="https://raw.githubusercontent.com/Guitx-l/Alchemist_Coders/refs/heads/main/media/ffrob.jpg" width=150>
<img src="https://raw.githubusercontent.com/Guitx-l/Alchemist_Coders/refs/heads/main/media/logo-kastler.png" width=150>
<img src="https://raw.githubusercontent.com/Guitx-l/Alchemist_Coders/refs/heads/main/media/robocup-junior.jpg" width=150>
</p>

Nous sommes, avec Botbusters, les équipes représentant le lycée [Alfred Kastler](https://lyceekastler.fr)
dans la [RoboCup Junior](https://www.robocup.fr/qu-est-ce-que-c-est) en ligue [SCT](https://www.robocup.fr/about-3).
Notre équipe est composée de [Guitx](https://github.com/Guitx-l) et de [Mamba](https://github.com/Jonathan-Mamba).
Ce dépôt contient un programme complet contenant des comportemements et des stratégies qui guideront les robots en fonction de situation précise sur le terrain pour avoir l'avantage sur l'équippe adverse.

# Nos résultats

|                              compétition                               |            date            | classement |
|:----------------------------------------------------------------------:|:--------------------------:|:----------:|
| [Robocup Académique](https://competition.robot-soccer-kit.com/team/1)  |         10/04/2025         |    2eme    |
|  [Robocup Nationale](https://competition.robot-soccer-kit.com/team/3)  |  31/05/2025 -> 01/06/2025  |    2eme    |
| [Robocup Européenne](https://competition.robot-soccer-kit.com/team/4)  |  04/06/2025 -> 07/06/2025  |     X      |

# Installation

- cloner le dépot
- installer python 3.12 ou 3.13
- installer la bibliothèque rsk:
  - sans game-controller:
        ```bash
        pip install robot-soccer-kit
        ```
  - avec game-controller:
        ```bash
        pip install robot-soccer-kit[gc]
        ```

  - > [Voir la documentation de la librairie pour plus d'informations](#documentation)

# Documentation

- [Documentation de la librairie robot-soccer-kit](https://robot-soccer-kit.github.io/documentation)
- [Dépôt github de la librairie robot-soccer-kit](https://github.com/robot-soccer-kit/robot-soccer-kit)

## Structure du dépôt

- [`src/`](src/) — code source principal
  - [`bot`](src/bot/) — shooter, gardien, multi-client et autres auxiliaires  
  - [`util/`](src/util/) — math, logging, démarrage du client  
  - [`test/`](src/test/) — srcipt servant au débogage de différentes fonctionnalités, peut avoir des pépendances différentes
  - [`__main__.py`](src/__main__.py) — point d'entrée du programme, exemple qui lance les deux robots

## Exécution du projet

Depuis la racine du dépôt:
```bash
python ./src --host 127.0.0.1 --key <KEY> --team {blue, green}
```

_Voir la documentation de la bibliothèque pour plus d'informations._

## Fonctionnement général - résumé

- Le code est organisé autour de fonctions d'update appelées en boucle par `start_client()`
- L'état est stocké dans des dicts simples retournés par des fonctions:
  - `get_shooter_dict()`
  - `get_keeper_dict()`
  - `get_multi_bot_dict()`
  - `...`
- Les fonctions d'update utilisent des paramètres explicites: (client, team, number, data_dict)
- Fonctions utilitaires disponibles:
  - `get_ball(client)`
  - `get_robot(client, team, number)`
  - `get_goal_sign(client, team)`
  - `...`

## Fonctionnement général - détaillé

- <u>Architecture principale</u>:
  Le programme est organisé autour de fonctions d'update appelées en boucle par `start_client()`. Chaque bot est exécuté avec la signature:
  `update_func(client, team, number, data_dict)`
  où:
  - `client`: connexion au game_controller
  - `team`: "blue" ou "green"
  - `number`: numéro du robot (1 ou 2)
  - `data_dict`: dictionnaire d'état fourni par get_*_dict()

- <u>Démarrage des clients</u>:  
  Utiliser `start_client(update_func, number, data_dict)` pour lancer un client. `__main__.py` montre un [exemple](src/__main__.py) qui lance deux threads (un pour chaque robot).

- <u>Gestion de l'état</u>:  
  L'état des comportements est stocké dans de simples dictionnaires (`get_shooter_dict()`, `get_keeper_dict()`, `get_multi_bot_dict()`, ...).

- <u>Décision multi-robot</u>:  
  `multi_update()` choisit si un robot agit comme buteur ou un gardien en appelant `is_shooter(client, team, number, goal_sign, ball)`. La sélection se base sur les positions relatives et l'état du jeu.

- <u>Comportements principaux</u>:  
  - `shooter_update()` : positionne le robot pour tirer et gère l'évitement de la règle du "ball abuse", le positionnement de tir et l'action de kick.  
  - `goalkeeper_update()` : calcule la meilleure position défensive, suit la trajectoire de la balle et effectue les dégagements/kicks si nécessaire.

- <u>Fonctions utilitaires</u>:  
  Fonctions utiles disponibles pour simplifier l'accès aux données du client:
  - `get_ball(client)`: retourne la position actuelle de la balle (copie).
  - `get_robot(client, team, number)`: retourne le robot et vérifie qu'il a une position.
  - `get_goal_sign(client, team)`: signe du but selon l'orientation de l'équipe.
  - -> Ces fonctions réduisent le nombre d'accès directs à client.robots et clarifient le flux de données.

- <u>Robustesse et erreurs</u>:  
  `start_client()` intercepte les exceptions `rsk.client.ClientError` et logge proprement les erreurs. Les fonctions d'update doivent lever ces erreurs si des données critiques (ex. position de la balle ou du robot) sont manquantes.
- <u>Conseils pour débutants</u>:  
  - Lire d'abord les `get_*_dict()` pour comprendre quelles clés sont attendues dans data_dict.  
  - Tester chaque update.  
  - Ajouter des petites docstrings et logs si un comportement semble obscur.

## Exemple en code

```py
from src.bot.multi_client import multi_update, get_multi_bot_dict
from src.util.init import start_client

start_client(multi_update, number=1, data_dict=get_multi_bot_dict())
```
