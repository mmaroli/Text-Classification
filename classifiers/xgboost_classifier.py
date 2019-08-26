import os
import json
import pandas as pd
import xgboost as xgb
from utilities.dataloader import XGBoostLoader


class XGBoostClassifier:
    def __init__(self, level, epochs):
        self.label_level = level
        self.num_epochs = epochs
        self.model_path = f'./models/xgboost_{self.label_level}.model'
        self.num_classes = len(json.load(open('./data/mapping.json')))
        self.training_params = {'objective': 'multi:softmax',
                                'num_class': self.num_classes,
                                'tree_method': 'hist',
                                'predictor': 'cpu_predictor'
                                }
        self.train_data = './data/traindata.parquet'
        self.val_data = './data/valdata.parquet'
        self.test_data = './data/testdata.parquet'
        self.data_loader = XGBoostLoader(level=self.label_level)

    def prepare_training_data(self):
        """ Prepares training, validation, and test data in parquet format """
        self.data_loader.prepare()

    def fit_tfidf(self):
        """ Fits tfidf vectorizer to training data """
        print("Fitting tfidf...")
        df = pd.read_parquet(self.train_data, columns=['_id', 'text', f'{self.label_level}_labels'])
        self.data_loader.embedding(df, train=True)

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
        chunk_val, chunk_labels = self.data_loader.embedding(chunk, train=False)
        xg_val = xgb.DMatrix(chunk_val, label=chunk_labels)
        return xg_val

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
            chunk_train, chunk_labels = self.data_loader.embedding(chunk, train=False)
            yield chunk_train, chunk_labels


    def train(self):
        """ Train XG Boost Model """
        xg_val = self.one_chunk()
        for epoch in range(self.num_epochs):
            print(f"Epochs: {epoch+1}/{self.num_epochs}...")
            for iter, (chunk_train, chunk_labels) in enumerate(self.get_chunks()):
                print(f"Iteration: {iter+1}/100...")
                xg_train = xgb.DMatrix(chunk_train, label=chunk_labels)
                evallist = [(xg_val, 'val'), (xg_train, 'train')]
                if not os.path.exists(self.model_path):
                    model = xgb.train(self.training_params, xg_train, 10, evallist)
                else:
                    model = xgb.train(self.training_params, xg_train, 10, evallist, xgb_model=self.model_path)
                model.save_model(self.model_path)
