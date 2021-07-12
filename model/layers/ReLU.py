import numpy

from model.layers.layer import Layer, LayerType
import numpy as np

class ReLU(Layer):

    def __init__(self):
        super().__init__()
        self.layer_type = LayerType.RELU
        self.output = None

    def setup(self, input_shape: tuple) -> None:
        self.input_shape = input_shape
        self.output_shape = input_shape

    def forward(self, input_layer: numpy.ndarray) -> numpy.ndarray:
        self.output: np.ndarray = np.maximum(0, input_layer)
        return self.output

    def backpropagation(self, d_score: np.ndarray) -> np.ndarray:
        d_score[self.output <= 0] = 0
        return d_score
