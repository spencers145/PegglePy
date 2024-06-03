import controller_templates
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