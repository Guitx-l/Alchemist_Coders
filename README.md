<h1 style="text-align: center">Alchemist Coders</h1>

<p style="text-align: center; font-style: italic">L'esprit du jeu, l'alchimie du code et de la stratégie</p>

<p style="text-align: center">
<img src="https://raw.githubusercontent.com/Guitx-l/Alchemist_Coders/refs/heads/main/media/ffrob.jpg" width=150>
<img src="https://raw.githubusercontent.com/Guitx-l/Alchemist_Coders/refs/heads/main/media/logo-kastler.png" width=150>
<img src="https://raw.githubusercontent.com/Guitx-l/Alchemist_Coders/refs/heads/main/media/robocup-junior.jpg" width=150>
</p>

Nous sommes, avec Botbusters, les équipes représentant le lycée [Alfred Kastler](https://lyceekastler.fr)
dans la [RoboCup Junior](https://www.robocup.fr/qu-est-ce-que-c-est) en ligue [SCT](https://www.robocup.fr/about-3).
Notre équipe est composée de [Guitx](https://github.com/Guitx-l) et de [Mamba](https://github.com/Jonathan-Mamba).
Ce dépôt contient un programme complet contenant des comportements et des stratégies qui guideront les robots en fonction de situations précises sur le terrain pour avoir l'avantage sur l'équipe adverse.

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
 > Il est fortement recommandé de lire la documentation de la librairie pour comprendre les différentes fonctionnalités et comment les utiliser efficacement dans votre code.

## Structure du dépôt

- [`src/`](src/) — code source principal
  - [`bot`](src/bot/) — shooter, gardien, multi-client et autres auxiliaires  
  - [`util/`](src/util/) — math, logging, démarrage du client  
  - [`test/`](src/test/) — scripts de test et débogage de différentes fonctionnalités, peut avoir des dépendances différentes
  - [`__main__.py`](src/__main__.py) — point d'entrée du programme, exemple qui lance les deux robots

## Exécution du projet

Depuis la racine du dépôt:
```bash
python ./src --host 127.0.0.1 --key <KEY> --team {blue, green}
```

_Voir la documentation de la bibliothèque pour plus d'informations._

## Fonctionnement général - résumé

- Le code est organisé autour de fonctions d'update appelées en boucle par `start_client()`
- L'état est stocké dans de simples dictionnaires retournés par des fonctions:
  - `get_shooter_dict()`
  - `get_keeper_dict()`
  - `get_role_manager_dict()`
  - `...`
- Les fonctions d'update utilisent des paramètres explicites: `(client, team, number, goal_sign, ball, data_dict)`
- Fonctions utilitaires disponibles dans `util.bot`:
  - `get_robot(client, team, number)` — retourne le robot avec validation de position
  - `can_play(bot, referee)` — vérifie si le robot peut jouer (non pénalisé)

## Fonctionnement général - détaillé

- <u>Architecture principale</u>:
  Le programme est organisé autour de fonctions d'update appelées en boucle par `start_client()`. Chaque bot est exécuté avec la signature:
  `update_func(client, team, number, goal_sign, ball, data_dict)`
  où:
  - `client`: connexion au game_controller
  - `team`: "blue" ou "green"
  - `number`: numéro du robot (1 ou 2)
  - `goal_sign`: -1 ou 1 (orientation du but adverse)
  - `ball`: position actuelle de la balle [x, y]
  - `data_dict`: dictionnaire d'état persistant fourni par `get_*_dict()`

- <u>Démarrage des clients</u>:  
  Utiliser `start_client(update_func, number, data_dict)` pour lancer un client. `__main__.py` montre un [exemple](src/__main__.py) qui lance deux threads (un pour chaque robot).

- <u>Gestion de l'état</u>:  
  L'état des comportements est stocké dans de simples dictionnaires (`get_shooter_dict()`, `get_keeper_dict()`, `get_role_manager_dict()`, ...).

- <u>Décision multi-robot</u>:  
  `role_manager_update()` choisit si un robot agit comme buteur ou un gardien en appelant `is_shooter(client, team, number, goal_sign, ball)`. La sélection se base sur les positions relatives des robots et leur disponibilité.

- <u>Comportements principaux</u>:  
  - `shooter_update()` : positionne le robot pour tirer et gère l'évitement de la règle du "ball abuse", le positionnement de tir et l'action de kick.  
  - `goalkeeper_update()` : calcule la meilleure position défensive, suit la trajectoire de la balle et effectue les dégagements si nécessaire.

- <u>Fonctions utilitaires (src.util.math)</u>:  
  Fonctions mathématiques pour les calculs géométriques:
  - `faces_ball(robot, ball, margin)`: vérifie si le robot pointe vers la balle
  - `is_inside_circle(point, center, radius)`: point dans un cercle
  - `is_inside_court(pos)`: position dans les limites du terrain
  - `angle_of(vector)`: angle d'un vecteur
  - `normalized(vector)`: normalise un vecteur
  - `get_shoot_position(goal_pos, ball_pos, offset)`: calcule la position optimale pour tirer
  - `line_intersects_circle(...)`: intersection ligne-cercle
  - `project_on_line(...)`: projection d'un point sur une ligne

- <u>Prédiction de la balle (src.bot.ball_anticipation)</u>:  
  Module spécialisé pour anticiper la trajectoire future de la balle:
  - `get_ball_velocity(client)`: vitesse actuelle de la balle
  - `get_ball_acceleration(client)`: accélération de la balle
  - `get_dynamic_future_ball(client)`: position prédite avec ajustement du latency
  - Détecte automatiquement les tirs (kick detection) et ignore les artefacts d'accélération

- <u>Robustesse et erreurs</u>:  
  `start_client()` intercepte les exceptions `rsk.client.ClientError` et les logge proprement. Les fonctions d'update doivent lever ces erreurs si des données critiques (ex. position du robot) sont manquantes.

- <u>Conseils de développement</u>:  
  - Lire d'abord les `get_*_dict()` pour comprendre quelles clés sont attendues dans `data_dict`
  - Utiliser `get_logger("nom_module")` pour les logs formatés avec couleurs
  - Tester avec `src/test/` pour déboguer isolément
  - Consulter `rsk_llm_docs.md` pour la documentation complète de la librairie rsk

## Exemple d'utilisation

### Lancer les deux robots avec gestion des rôles (défaut)
```bash
python ./src --team blue --host 127.0.0.1 --key "YOUR_KEY"
```

### Lancer un robot personnalisé
```python
from src.bot.role_manager import role_manager_update, get_role_manager_dict
from src.util.init import start_client

# Lance le robot 1 avec la stratégie de gestion des rôles
start_client(role_manager_update, number=1, data_dict=get_role_manager_dict())
```

### Lancer le shooter seul (test)
```python
from src.bot.shooter import shooter_update, get_shooter_dict
from src.util.init import start_client

start_client(shooter_update, number=1, data_dict=get_shooter_dict())
```
