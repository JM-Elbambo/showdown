import asyncio
import json
import logging
import traceback
from copy import deepcopy

from bot_config import BotConfig
from config import ShowdownConfig, init_logging

from teams import load_team
from showdown.run_battle import pokemon_battle
from showdown.websocket_client import PSWebsocketClient

from data import all_move_json
from data import pokedex
from data.mods.apply_mods import apply_mods


POKEMON_MODE = "gen8ou"
LOG_LEVEL = "INFO"
WEBSOCKET_URI = "wss://sim3.psim.us/showdown/websocket"
RUN_COUNT = 1

logger = logging.getLogger(__name__)


def check_dictionaries_are_unmodified(original_pokedex, original_move_json):
    # The bot should not modify the data dictionaries
    # This is a "just-in-case" check to make sure and will stop the bot if it mutates either of them
    if original_move_json != all_move_json:
        logger.critical("Move JSON changed!\nDumping modified version to `modified_moves.json`")
        with open("modified_moves.json", 'w') as f:
            json.dump(all_move_json, f, indent=4)
        exit(1)
    else:
        logger.debug("Move JSON unmodified!")

    if original_pokedex != pokedex:
        logger.critical(
            "Pokedex JSON changed!\nDumping modified version to `modified_pokedex.json`"
        )
        with open("modified_pokedex.json", 'w') as f:
            json.dump(pokedex, f, indent=4)
        exit(1)
    else:
        logger.debug("Pokedex JSON unmodified!")


async def showdown(config:BotConfig, user_to_challenge:str=None):
    init_logging(LOG_LEVEL, False)
    apply_mods(POKEMON_MODE)

    original_pokedex = deepcopy(pokedex)
    original_move_json = deepcopy(all_move_json)

    ps_websocket_client = await PSWebsocketClient.create(
        config.username,
        config.password,
        WEBSOCKET_URI
    )
    await ps_websocket_client.login()

    battles_run = 0
    wins = 0
    losses = 0
    while True:
        team = load_team(config.team_file)
        
        if user_to_challenge == None or user_to_challenge == "":
            await ps_websocket_client.accept_challenge(
                POKEMON_MODE,
                team,
                None
            )
        else:
            await ps_websocket_client.challenge_user(
                user_to_challenge,
                POKEMON_MODE,
                team
            )
        
        winner = await pokemon_battle(ps_websocket_client, POKEMON_MODE)
        if winner == config.username:
            wins += 1
        else:
            losses += 1

        logger.info("W: {}\tL: {}".format(wins, losses))
        check_dictionaries_are_unmodified(original_pokedex, original_move_json)

        battles_run += 1
        if battles_run >= RUN_COUNT:
            break


if __name__ == "__main__":
    try:
        asyncio.run(showdown())
    except Exception as e:
        logger.error(traceback.format_exc())
        raise
