import random

class Network:
    def __init__(self, layers: int, layer_sizes: list[int]):
        self.layers = []
        self.weights = []
        for _ in range(0, layers):
            self.addLayer(layer_sizes)

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

    def update(self):
        for i in range(1, len(self.layers)):
            for j in range(0, len(self.layers[i])):
                self.layers[i][j] = 0
                for k in range(0, len(self.layers[i-1])):
                    self.layers[i][j] += self.layers[i-1][k] * self.weights[i][j][k]

    def readOutput(self) -> list[float]:
        return self.layers[-1]
    
    def getInputSize(self) -> int:
        return len(self.layers[0])