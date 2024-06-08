class GameState:
    def __init__(self, pegs: list, ball_count: int, score: int, bucket_pos: float, bucket_velocity: float):
        self.PEGS = pegs
        self.BALLS = ball_count
        self.SCORE = score
        self.BUCKET_POS = bucket_pos
        self.BUCKET_VELOCITY = bucket_velocity