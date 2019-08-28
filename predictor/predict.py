import pickle
import numpy as np
import tensorflow as tf



class Predictor:
    def __init__(self):
        self.mapping_file = './data/mapping.pickle'
        self.model_path = './tensorflow_subsubcat.model'
        self.mapping = self.read_mapping()
        self.model = tf.keras.models.load_model(self.model_path)

    def read_mapping(self):
        with open(self.mapping_file, 'rb') as f:
            mapping = pickle.load(f)
        return mapping


    def classify(self, text):
        pred = self.model.predict(np.array([text]))
        amax = pred.argmax()
        cat, subcat, subsubcat = self.mapping[amax].split('/')
        response = {}
        response['prediction'] = self.mapping[amax]
        response['score'] = str(pred[0][amax])
        response['cat'] = cat
        response['subcat'] = subcat
        response['subsubcat'] = subsubcat
        response['ad_cat_arr'] = self.mapping[amax].split('/')
        return response
