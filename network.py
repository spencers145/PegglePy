import random, numpy

def listToWeights(weight_list: list[float], layer_sizes: list[int]) -> list[list[list[float]]]:
    weights = []
    index = 0

    for i in range(0, len(layer_sizes)):
        this_layer_weights = []
        if i > 0:
            for _ in range(0, layer_sizes[i]):
                sub_weights = []
                for _ in range(0, layer_sizes[i - 1]):
                    sub_weights.append(weight_list[index])
                    index += 1
                this_layer_weights.append(sub_weights)
        else:
            for _ in range(0, layer_sizes[0]):
                this_layer_weights.append([1])
        weights.append(this_layer_weights)
    return weights

def weightsToList(weights: list[list[list[float]]]) -> list[float]:
    weights_list = []
    for i in range(1, len(weights)):
        for j in range(0, len(weights[i])):
            for k in range(0, len(weights[i][j])):
                weights_list.append(weights[i][j][k])
    return weights_list

class Network:
    def __init__(self, layer_sizes: list[int], activation_type: str):
        self.layers = []
        self.weights = []
        for _ in range(0, len(layer_sizes)):
            self.addLayer(layer_sizes)
        
        self._UPDATE_FUNCTION = self._getUpdateFunction(activation_type)

    def addLayer(self, layer_sizes):
        current_layer = len(self.layers)
        current_size = layer_sizes[current_layer]

        if current_layer > 0:
            node_weights = [0] * layer_sizes[current_layer - 1]
        else: node_weights = [1]

        self_layer = []
        for _ in range(0, current_size):
            self_layer.append(node_weights.copy())
        self.weights.append(self_layer)
        self.layers.append([0] * current_size)

    def jostleSelf(self, magnitude):
        for i in range(1, len(self.weights)):
            for j in range(0, len(self.weights[i])):
                for k in range(0, len(self.weights[i][j])):
                    self.weights[i][j][k] += magnitude * (random.random() - 0.5)
    
    def setWeights(self, weights_obj: list[list[list[int]]]):
        assert len(self.weights) == len(weights_obj), "Tried to set weights object with the wrong structure."
        for i in range(1, len(self.weights)):
            assert len(self.weights[i]) == len(weights_obj[i]), "Tried to set weights object with the wrong structure."
            for j in range(0, len(self.weights[i])):
                assert len(self.weights[i][j]) == len(weights_obj[i][j]), "Tried to set weights object with the wrong structure."
                for k in range(0, len(self.weights[i][j])):
                    self.weights[i][j][k] = weights_obj[i][j][k]
    
    def updateInputs(self, input: list[float]):
        assert len(self.layers[0]) == len(input), "Input list length does not match network input length!"
        self.layers[0] = input

    def _getUpdateFunction(self, activation_type: str):
        match activation_type:
            case "linear":
                return self.linearUpdate
            case "sigmoid":
                return self.sigmoidUpdate
            case "relu":
                return self.reluUpdate
            case "leaky_relu":
                return self.leakyReluUpdate
            case "swish":
                return self.swishUpdate
            case _:
                raise "Invalid neuron activation type."

    def update(self):
        for i in range(1, len(self.layers)):
            for j in range(0, len(self.layers[i])):
                self.layers[i][j] = 0
                for k in range(0, len(self.layers[i-1])):
                    self.layers[i][j] += self.layers[i-1][k] * self.weights[i][j][k]
                self._UPDATE_FUNCTION(i, j)

    def linearUpdate(self, _, __): pass
    
    def sigmoidUpdate(self, i, j):
        self.layers[i][j] = 1/(1 + numpy.exp(-self.layers[i][j]))
    
    def reluUpdate(self, i, j):
        if self.layers[i][j] < 0:
            self.layers[i][j] = 0
    
    def leakyReluUpdate(self, i, j):
        if self.layers[i][j] < 0:
            self.layers[i][j] *= 0.01
    
    def swishUpdate(self, i, j):
        self.layers[i][j] = self.layers[i][j]/(1 + numpy.exp(-self.layers[i][j]))

    def readOutput(self) -> list[float]:
        return self.layers[-1]
    
    def getInputSize(self) -> int:
        return len(self.layers[0])