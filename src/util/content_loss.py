import tensorflow as tf


class Evaluator:
    def __init__(self):
        model = tf.keras.applications.VGG19()

        # Strip layers off of the model
        # We are only interested in feature maps, not the actual output
        self.model = tf.keras.Model(inputs=model.input, outputs=model.layers[-6].output)

        # Get the TensorShape of the input layer and convert it to a Tensor
        # We drop the first element of the list because it is None
        # We drop the last element because it represents the number of channels
        input_tensor_shape = self.model.layers[0].input.shape.as_list()
        self.input_shape = input_tensor_shape[1:-1]

    def preprocess_input(self, image: tf.Tensor) -> tf.Tensor:
        """Preprocess the image for input to the model."""
        image = tf.keras.applications.vgg19.preprocess_input(image)
        image = tf.image.resize(image, self.input_shape)
        return tf.expand_dims(image, axis=0)

    def get_content_loss(self, image_1: tf.Tensor, image_2: tf.Tensor) -> float:
        """Compute the Euclidean distance between the high level features of two images."""
        image_1 = self.preprocess_input(image_1)
        image_2 = self.preprocess_input(image_2)
        return tf.sqrt(tf.reduce_sum(tf.math.squared_difference(self.model(image_1), self.model(image_2))))


def read_image_file(filename: str) -> tf.Tensor:
    raw = tf.io.read_file(filename)
    return tf.image.decode_jpeg(raw)


if __name__ == '__main__':
    evaluator = Evaluator()
    print(evaluator.model.summary())

    # Read the files
    import os
    cwd = os.getcwd()
    img_1 = read_image_file(cwd + "/../../img/test4.jpg")
    img_2 = read_image_file(cwd + "/../../img/test5.jpg")

    # Get the loss
    loss = evaluator.get_content_loss(img_1, img_2)
    print('Loss:', loss)
