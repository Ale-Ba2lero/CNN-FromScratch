from model.loss import CategoricalCrossEntropy, Loss
from model.layers.layer import Layer, LayerType
from model.utility import Metrics

from sklearn.model_selection import train_test_split
import numpy as np
from tqdm import tqdm


class Model:
    def __init__(self, layers: list, loss_function: Loss = CategoricalCrossEntropy()) -> None:
        self.layers = layers
        self.loss_function = loss_function
        self.metrics = None

    def train(self,
              dataset: np.ndarray,
              labels: np.ndarray,
              epochs: int = 1,
              batch_size: int = 1,
              step_size: float = 1e-2):

        self.metrics = Metrics()

        X_train, X_val, y_train, y_val = train_test_split(dataset,
                                                          labels,
                                                          test_size=0.1,
                                                          random_state=6)

        n_batches: int = len(X_train) // batch_size
        extra_batch: int = int(len(X_train) % batch_size > 0)

        print(f'training set size: {len(X_train)}')
        print(f'evaluation set size: {len(X_val)}')
        print(f'epochs: {epochs}')
        print(f'batch size: {batch_size}')
        print(f'batches: {n_batches}\nextra batch: {extra_batch}\n')

        for layer_idx in range(len(self.layers)):
            self.layer_setup(self.layers[layer_idx], layer_idx, dataset[0].shape)

        for epoch in range(epochs):
            """
            l, loss, num_correct, acc=0
            """
            for j in tqdm(range(n_batches + extra_batch)):
                """
                if j > 0 and j % 100 == 99:
                    print_loss = "{:.2}".format(l / 100)
                    print_acc = "{:.2%}".format(num_correct / 100)
                    print(f"\nepoch {i + 1} iteration {j + 1}: loss {print_loss} |  acc {print_acc}")
                    loss = 0
                    num_correct = 0
                """
                X_batch = X_train[j * batch_size:(j + 1) * batch_size]
                y_batch = y_train[j * batch_size:(j + 1) * batch_size]

                output = self.forward(X_batch)
                _, _, d_score = self.loss_function.calculate(output, y_batch)
                """
                l += loss
                num_correct += acc
                """
                self.backward(d_score, step_size)

            train_loss, train_acc = self.metrics.evaluate_model(X_train, y_train, self.layers, self.loss_function)
            self.metrics.update(train_loss, train_acc, "train")

            # self.metrics.metrics_log(train_loss, train_acc, text=f"Epoch {epoch+1} / {epochs}")

            eva_loss, eva_acc = self.metrics.evaluate_model(X_val, y_val, self.layers, self.loss_function)
            self.metrics.update(eva_loss, eva_acc, "val")

    def forward(self, inputs):
        output = inputs
        for layer in self.layers:
            output = layer.forward(output)
        return output

    def backward(self, d_score, step_size):
        for layer in reversed(self.layers):
            d_score = layer.backpropagation(d_score=d_score)

        # layer update
        for layer in self.layers:
            if layer.layer_type == LayerType.CONV or layer.layer_type == LayerType.DENSE:
                layer.update(step_size)

    def layer_setup(self, layer: Layer, layer_idx: int, input_shape: tuple):
        layer.id_ = layer_idx
        if layer.layer_type == LayerType.DENSE:
            if layer_idx == 0:
                self.layers[layer_idx].setup(input_shape=input_shape[0], next_layer=self.layers[layer_idx + 1])
            else:
                dense_input_shape = self.layers[layer_idx - 1].output_shape
                if type(self.layers[layer_idx - 1].output_shape) == tuple:
                    dense_input_shape = dense_input_shape[0]
                if layer_idx == len(self.layers) - 1:
                    self.layers[layer_idx].setup(input_shape=dense_input_shape)
                else:
                    self.layers[layer_idx].setup(input_shape=dense_input_shape, next_layer=self.layers[layer_idx + 1])
        elif layer.layer_type == LayerType.CONV and layer_idx == 0:
            self.layers[layer_idx].setup(input_shape=input_shape)
        else:
            self.layers[layer_idx].setup(input_shape=self.layers[layer_idx - 1].output_shape)