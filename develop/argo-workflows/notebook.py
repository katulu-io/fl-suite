from fl_suite import pipelines


@pipelines.fl_client(packages=["tensorflow", "flwr"])
def mnist_client():
    import flwr as fl
    import tensorflow as tf

    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(10),
    ])
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])

    class MNISTClient(fl.client.NumPyClient):
        def get_parameters(self):
            return model.get_weights()

        def fit(self, parameters, config):
            model.set_weights(parameters)
            model.fit(x_train, y_train, epochs=1, batch_size=32)
            return model.get_weights(), len(x_train), {}

        def evaluate(self, parameters, config):
            model.set_weights(parameters)
            loss, accuracy = model.evaluate(x_test, y_test)
            return loss, len(x_test), {"accuracy": accuracy}

    fl.client.start_numpy_client("localhost:9080", client=MNISTClient())


pipelines.build(mnist_client, registry="localhost:5000", verify_registry_tls=False)
