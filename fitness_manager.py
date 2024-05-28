import json

def getHighestScoringPlayer(generation: list[tuple[int, any]]) -> tuple[int, any]:
    biggest = 0
    for i in range(0, len(generation)):
        if generation[i][0] > generation[biggest][0]: biggest = i
    return generation.pop(biggest)

# # universal fitness function
# def scorePlayer(manager: battle_manager.Manager, player_id: str) -> int:
#     score = 0
#     for game_id in manager.results.keys():
#         # only judge the model if it survives the game (0 points for losing)
#         if player_id in manager.results[game_id]:
#             # severely punish stalling out games (a.k.a. at least one other player survived with it)
#             if len(manager.results[game_id]) != 1: score -= 5
#             # reward winning games (a.k.a. only it survived)
#             else: score += 1
#     return score
