import network, peggle_manager, fitness_manager, math, random

def minimizeFunction(guess: list[float], number_of_games: int, layer_sizes: list[int], network_controller_template, activation_type: str, options = {}):
    weights = network.listToWeights(guess, layer_sizes)
    #print("minimize called")
    return -testNetworkFromWeights(weights, number_of_games, layer_sizes, network_controller_template, activation_type, options)

def testNetworkFromWeights(weights: list[list[list[float]]], number_of_games: int, layer_sizes: list[int], network_controller_template, activation_type: str, options = {}):
    manager = peggle_manager.Manager()
    network_to_test = network.Network(layer_sizes, activation_type)
    network_to_test.setWeights(weights)

    #print(weights)

    test_out = testNetworks(manager, number_of_games, [(0, network_to_test)], network_controller_template, options)
    # only print a small fraction of the debug messages
    if random.random() > 0.99: print("score: %.2f" %(test_out[0][0]))
    return test_out[0][0]

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
             options = {},
             total_tests = 0) -> tuple[int, network.Network]:
    manager.wipeHistory()
    manager.wipeResults()

    games = []
    # make a new player from the template
    for i in range(0, len(generation)):
        network = generation[i][1]
        player = network_controller_template("controller_n%d" %(i), network)
        games.append((player, number_of_games_each))

    if "color_map" in options and total_tests:
        original_color_map = options["color_map"].copy()
        for _ in range(total_tests):
            # discard all the maps we've already used this generation
            options["color_map"].pop(0)
    
    if "level_map" in options and total_tests:
        original_level_map = options["level_map"].copy()
        for _ in range(total_tests):
            options["level_map"].pop(0)
    
    manager.runGames(games, options)
        
    if "color_map" in options and total_tests: options["color_map"] = original_color_map
    if "level_map" in options and total_tests: options["level_map"] = original_level_map

    for game_id in manager.results.keys():
        # extract the index of the network we're dealing with
        controller_index = int(game_id.split("_")[1][1:])
        network_score = math.sqrt(manager.results[game_id]["score"])
        generation[controller_index] = (generation[controller_index][0] + network_score, generation[controller_index][1])

    return generation

def trainNetwork(generations: int,
                    generation_size: int,
                    base_tests_per_child: int,
                    layer_sizes: list[int],
                    network_controller_template,
                    activation_type: str,
                    options = {},
                    verbose = False,
                    debug = False) -> tuple[float, network.Network, dict, dict]:
    manager = peggle_manager.Manager()
    # set our seed
    seed = (0, network.Network(layer_sizes, activation_type))

    for i in range(1, generations + 1):
        generation = []

        # while using a color map, shuffle every generation
        if "color_map" in options:
            random.shuffle(options["color_map"])
        
        if "level_map" in options:
            random.shuffle(options["level_map"])

        # first, generate a lot of randomly jostled networks
        # if this is the first generation, make 10x more than usual
        for j in range(0, (10 * generation_size if i == 1 else generation_size)):
            # make a new network based on the seed
            child_network = network.Network(layer_sizes, activation_type)
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
            tests = round(base_tests_per_child * 2**(step - 1))
            total_tests += tests

            step_generation = testNetworks(manager, tests, generation, network_controller_template, options, total_tests = total_tests)
            generation = []

            # debug code that activates if verbose is on
            # tells about the scores of contestants in the training process for each round
            if debug and verbose:
                debug_scores = []
                for child in step_generation:
                    debug_scores.append(child[0])

                debug_sum = 0
                for score in debug_scores: debug_sum += score

                debug_scores.sort(reverse=True)
                print(debug_scores)
                print("gen %d step %d average: %.2f" %(i, step, debug_sum/len(step_generation)/total_tests))

            # pop off the best math.ceil(len(generation)/(2*step)) players
            while len(generation) < target_survivor_count:
                best = fitness_manager.getHighestScoringPlayer(step_generation)
                generation.append(best)

        # get our new seed and loop back
        seed = generation[0]

        # optional debug info about the seed we just trained
        # keeps track of the networks between generations
        if debug:
            print("generation %d final proficiency: %.2f" %(i, seed[0]/total_tests))
            print("---------------")

    if verbose:
        print("TRAINING PARAMETERS:")
        print("Generations: %d" %(generations))
        print("Children tested per generation: %d" %(generation_size))
        print("Base # of test-games per child: %d" %(base_tests_per_child))
        print("---------------")
        print("Balls used: %s" %(10 if "balls" not in options.keys() else options["balls"]))
        print("Color map used: %s" %("false" if "color_map" not in options.keys() else "true"))
        print("---------------")

    # get a final result to test the effectiveness of the model
    # do not let the color map leak into our testing data
    if "color_map" in options.keys():
        options.pop("color_map")
    score = testNetworks(manager, 100, [(0, seed[1])], network_controller_template, options)[0][0]

    if verbose:
        print("RESULTS:")
        print("Network proficiency: %.2f" %(score/100))

    return (score, seed[1], manager)