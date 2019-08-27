import tensorflow as tf
import tensorflow_hub as hub
from utilities.dataloader import NeuralLoader


class Neural:
    def __init__(self, level, epochs):
        self.label_level = level
        self.num_epochs = epochs
        self.num_classes = 194
        self.train_data = './data/traindata.parquet'
        self.val_data = './data/valdata.parquet'
        self.test_data = './data/testdata.parquet'
        self.model_path = f'./models/tensorflow_{self.label_level}.model'
        self.embedding_model = 'https://tfhub.dev/google/tf2-preview/nnlm-en-dim128/1'
        self.data_loader = NeuralLoader(level=self.label_level)

    def prepare_training_data(self):
        """ Prepares training, validation, and test data in parquet format """
        self.data_loader.prepare()

    def get_chunks_validation(self):
        """ Gets validation data in chunks

        Returns
        ---------
        val_generator: Generator
            Generator for eval data which generates df
        """
        return self.data_loader.load_parquet_chunks(file=self.val_data)

    def one_chunk(self):
        """ Use with `get_chunks_validation` """
        chunk_generator = self.get_chunks_validation()
        chunk = next(chunk_generator)
        chunk_val, chunk_labels = self.data_loader.embedding(chunk)
        return (chunk_val, chunk_labels)

    def get_chunks(self):
        """ Gets training data in chunks.

        Returns
        ---------
        chunk_train: np.array
            Numpy array with dimensions (m x d). m is number of articles and d
            is embedding dimensions.
        chunk_labels: pd.Series
            Series with dimensions (m x 1).
        """
        chunker = self.data_loader.load_parquet_chunks(file=self.train_data)
        for chunk in chunker:
            chunk_train, chunk_labels = self.data_loader.embedding(chunk)
            yield chunk_train, chunk_labels

    def build_model(self):
        hub_layer = hub.KerasLayer(self.embedding_model, input_shape=[], dtype=tf.string, trainable=True)
        model = tf.keras.Sequential()
        model.add(hub_layer)
        model.add(tf.keras.layers.Dense(64, activation='relu'))
        model.add(keras.layers.Dense(self.num_classes, activation='softmax'))
        model.summary()
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model


    def train(self):
        """ Train tensorflow model """
        val_data = self.one_chunk()
        model = self.build_model()
        for epoch in range(self.num_epochs):
            print(f"Epochs: {epoch+1}/{self.num_epochs}...")
            for iter, (chunk_train, chunk_labels) in enumerate(self.get_chunks()):
                print(f"Iteration: {iter+1}/100...")
                if not os.path.exists(self.model_path):
                    model.fit(x=chunk_train,
                              y=chunk_labels,
                              epochs=1,
                              validation_data=val_data,
                              verbose=1)
                else:
                    model = tf.keras.models.load_model(self.model_path)
                    model.fit(x=chunk_train,
                              y=chunk_labels,
                              epochs=1,
                              validation_data=val_data,
                              verbose=1)
                model.save(self.model_path)
