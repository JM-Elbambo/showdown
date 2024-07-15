import os
import json
import logging
import sys


logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for development and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


move_json_location = resource_path('data\\moves.json')
with open(move_json_location) as f:
    all_move_json = json.load(f)

pkmn_json_location = resource_path('data\\pokedex.json')
with open(pkmn_json_location, 'r') as f:
    pokedex = json.loads(f.read())

random_battle_set_location = resource_path('data\\random_battle_sets.json')
with open(random_battle_set_location, 'r') as f:
    random_battle_sets = json.load(f)


pokemon_sets = random_battle_sets
effectiveness = {}
team_datasets = None
