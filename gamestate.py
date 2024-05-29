from pegglepy.local.peg import Peg

class GameState:
    def __init__(self, pegs: list[Peg], ball_count: int, score: int):
        self.PEGS = pegs
        self.BALLS = ball_count
        self.SCORE = score