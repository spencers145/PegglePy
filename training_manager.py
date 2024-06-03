import network, peggle_manager, fitness_manager


def debugNetworkWeightSum(network: network.Network):
    sum = 0
    for a in network.weights:
        for b in a:
            for c in b:
                sum += abs(c)
    return sum

# run a number of games to test the effectiveness of the network we've trained
# return a score: the number of games won
def testNetworks(manager: peggle_manager.Manager,
             number_of_games_each: int,
             generation: list[tuple[int, network.Network]],
             network_controller_template,
             options = {}) -> tuple[int, network.Network]:
    manager.wipeHistory()
    manager.wipeResults()

    games = []
    # make a new player from the template
    for i in range(0, len(generation)):
        network = generation[i][1]
        player = network_controller_template("controller_n%d" %(i), network)
        games.append((player, number_of_games_each))

    manager.runGames(games, options)
    for game_id in manager.results.keys():
        # extract the index of the network we're dealing with
        controller_index = int(game_id.split("_")[1][1:])
        #print(manager.results[game_id])
        network_score = manager.results[game_id]["score"] * (1 if manager.results[game_id]["orange_pegs_left"] > 0 else 8)
        generation[controller_index] = (generation[controller_index][0] + network_score, generation[controller_index][1])

    return generation

def trainNetwork(generations: int,
                    generation_size: int,
                    base_tests_per_child: int,
                    layer_sizes: list[int],
                    network_controller_template,
                    options = {},
                    verbose = False,
                    debug = False) -> tuple[float, network.Network, dict, dict]:
    manager = peggle_manager.Manager()
    # set our seed
    seed = (0, network.Network(len(layer_sizes), layer_sizes))

    for i in range(1, generations + 1):
        generation = []
        # first, generate a lot of randomly jostled networks
        # if this is the first generation, make 10x more than usual
        for j in range(0, (10 * generation_size if i == 1 else generation_size)):
            # make a new network based on the seed
            child_network = network.Network(len(layer_sizes), layer_sizes)
            child_network.setWeights(seed[1].weights)
            # jostle amount as a function of how many generations (i) and which child (j)
            # effectively, i increase precision over time
            # and every generation, j produce more networks close to the seed, and less far away  
            magnitude = (j/10 if i == 1 else j)/i
            child_network.jostleSelf(magnitude**0.5)
            generation.append((0, child_network))

        total_tests = 0
        step = 0
        while len(generation) > 1:
            step += 1
            # list for networks and their scores during this step
            step_generation = []
            target_survivor_count = len(generation)/(2*step)

            # test each network. give them a score.
            # the # of tests increases as we refine our selection
            tests = 3 if step == 1 else round(base_tests_per_child * 2**(step - 2))
            total_tests += tests

            step_generation = testNetworks(manager, tests, generation, network_controller_template, options)
            generation = []

            # debug code that activates if verbose is on
            # tells about the scores of contestants in the training process for each round
            if debug and verbose:
                debug_scores = []
                for child in step_generation:
                    debug_scores.append(child[0])
                debug_scores.sort(reverse=True)
                print(debug_scores)

            # pop off the best math.ceil(len(generation)/(2*step)) players
            while len(generation) < target_survivor_count:
                best = fitness_manager.getHighestScoringPlayer(step_generation)
                generation.append(best)

        # get our new seed and loop back
        seed = generation[0]

        # optional debug info about the seed we just trained
        # keeps track of the networks between generations
        if debug:
            print("final proficiency: " + str(seed[0]/total_tests))
            print("---------------")

    # get a final result to test the effectiveness of the model
    score = testNetworks(manager, 50, [(0, seed[1])], network_controller_template, options)[0][0]

    # explicitly print results if we are verbose
    # if verbose:
    #     print("TRAINING PARAMETERS:")
    #     print("Generations: %d" %(generations))
    #     print("Children tested per generation: %d" %(generation_size))
    #     print("Base # of test-games per child: %d" %(base_tests_per_child))
    #     print("---------------")
    #     print("Schema used: %s" %(schema.NAME))
    #     print("Opponent count: %d" %(len(opponents)))
    #     print("---------------")
    #     print("RESULTS:")
    #     print("Network proficiency: %.3f" %(score/10000))
    #     print("Move distribution:")
    #     for move in moves.keys():
    #         print("%s: %.3f" %(move, moves[move]))

    return (score, seed[1], manager)