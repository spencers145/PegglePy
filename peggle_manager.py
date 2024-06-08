import controller_templates, random
from gamestate import *
from run_peggle_network import executeGameQueue

class Manager:
    def __init__(self):
        self.history = {}
        self.results = {}

    def runGames(self, games: list[tuple[controller_templates.Controller,int]], options = {}):
        results, history = executeGameQueue(games, options)
        for game_id in history.keys():
            self.history[game_id] = history[game_id]
            self.results[game_id] = results[game_id]

    def wipeResults(self):
        self.results = {}

    def wipeHistory(self):
        self.history = {}

def generateColorMap(length: int, peg_count: int) -> list[list]:
    color_map = []
    for _ in range(length):
        this_game_map = ["blue"] * peg_count
        target_oranges = 25
        target_greens = 2

        if peg_count < 27:
            target_oranges = 1 if peg_count <= 3 else peg_count - 2
            if peg_count <= 2:
                target_greens = peg_count - target_oranges

        peg_pool = list(range(0, peg_count))

        # create orange pegs
        for _ in range(target_oranges):
            peg_index = random.choice(peg_pool)
            peg_pool.remove(peg_index)
            this_game_map[peg_index] = "orange"

        # create green pegs
        for _ in range(target_greens):
            peg_index = random.choice(peg_pool)
            peg_pool.remove(peg_index)
            this_game_map[peg_index] = "green"
        
        color_map.append(this_game_map)
    
    return color_map