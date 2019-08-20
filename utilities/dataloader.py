import json
import numpy as np
import pandas as pd
import pyarrow as pa
import xgboost as xgb
import pyarrow.parquet as pq
from pymongo import MongoClient
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from utilities.json2text import TextReader


class DataLoader:
    def __init__(self, dataset):
        """ Creates dataset file containg text data for urls """
        self.dataset = dataset
        self.text_reader = TextReader()
        self.mongo_db = MongoClient('cme3-mongo01-qa.lv7.leaf.io')['cme']

    def access_element(self, arr, element):
        try:
            return arr[element]
        except IndexError:
            return None

    def segment_categories(self, arr):
        """ Given array, divide into category, subcategory, and subsubcategory """
        cat = arr[0]
        subcat = self.access_element(arr, 1)
        subsubcat = self.access_element(arr, 2)
        return cat,subcat,subsubcat

    def read_data(self):
        print("Querying mongo...")
        query = self.mongo_db.document.find({"type":"Article", "_type":"document", "ad_category": {"$exists": True} }, {"sections": 1, "ad_category": 1} )
        with open(self.dataset, 'w') as out:
            for i, doc in enumerate(query):
                text = self.text_reader.json2text(doc)[1]
                cat,subcat,subsubcat = self.segment_categories(doc['ad_category'])
                tmp_df = pd.DataFrame({'_id': [doc['_id']], 'text': [text], 'cat': [cat], 'subcat': [subcat], 'subsubcat': [subsubcat]})
                if i == 0:
                    tmp_df.to_csv(out, index=False)
                else:
                    tmp_df.to_csv(out, header=False, index=False)

    def read_data_parquet(self):
        print("Querying mongo...")
        query = self.mongo_db.document.find({"type":"Article", "_type":"document", "ad_category": {"$exists": True} }, {"sections": 1, "ad_category": 1} )
        ids = []
        texts = []
        cats = []
        subcats = []
        subsubcats = []
        for doc in query:
            text = self.text_reader.json2text(doc)[1].replace('\n', ' ')
            cat,subcat,subsubcat = self.segment_categories(doc['ad_category'])
            ids.append(doc['_id'])
            texts.append(text)
            cats.append(cat)
            subcats.append(subcat)
            subsubcats.append(subsubcat)
        tmp_df = pd.DataFrame({'_id': ids, 'text': texts, 'cat': cats, 'subcat': subcats, 'subsubcat': subsubcats})
        table = pa.Table.from_pandas(tmp_df)
        with open('./data/dataset.parquet', table.schema) as writer:
            writer.write_table(table)

    def convert_to_parquet(self, file, output):
        df = pd.read_csv(file)
        table = pa.Table.from_pandas(df)
        with pq.ParquetWriter(f'./data/{output}', table.schema) as writer:
            writer.write_table(table)





class XGBoostLoader:
    def __init__(self, level):
        self.level = level
        self.dataset = './data/dataset.csv'
        self.dataset_parquet = './data/dataset.parquet'
        self.encoder = LabelEncoder()
        self.vectorizer = TfidfVectorizer()


    def read_data(self):
        """ Reads data in chunks """
        data = pd.read_csv(self.dataset, chunksize=10000)
        return data

    def write_parquet(self, chunked_df, filename):
        """ Writes dataframe to parquet file """
        with pq.ParquetWriter(f'./data/{filename}', self.schema) as writer:
            for chunk in chunked_df:
                tmp_table = pa.Table.from_pandas(chunk)
                writer.write_table(tmp_table)

    def load_parquet_chunks(self, file):
        """ Loads parquet file in chunks

        Yields
        -----------
        parquet_chunk: pd.Dataframe

        """
        parquet_file = pq.ParquetFile(file)
        for chunk_num in range(parquet_file.num_row_groups):
            yield parquet_file.read_row_group(chunk_num).to_pandas()

    def write_mapping(self):
        """ Write label mapping to file """
        mapping = dict(zip(self.encoder.classes_, list(map(lambda x: str(x), self.encoder.transform(self.encoder.classes_) ) ) ))
        with open('./data/mapping.json', 'w', encoding='utf-8') as out:
            json.dump(mapping, out)


    def encode_labels(self):
        """ Adds a column to dataframe representing encoded labels

        Parameters
        -----------
        level: string
            String denoting cat, subcat, or subsubcat to encode

        Returns
        -----------
        df: pd.Dataframe
            Pandas dataframe with new column added
        """
        df = pd.read_parquet(self.dataset_parquet, columns=['_id', 'text', self.level])
        df.dropna(subset=[self.level], inplace=True)
        self.encoder.fit(df[self.level])
        self.write_mapping()
        df[f'{self.level}_labels'] = self.encoder.transform(df[self.level])
        self.schema = pa.Table.from_pandas(df).schema
        return df

    def split_dataset(self, df):
        """ Splits dataset into train-val-test

        Parameters
        -----------
        df: pd.Dataframe
            Dataframe containing entire dataset

        Returns
        ----------
        train_df: pd.Dataframe
            Train dataframe.
        val_df: pd.Dataframe
            Validation dataframe.
        test_df: pd.Dataframe
            Test dataframe.
        """
        train_df, val_df = train_test_split(df, test_size=0.3, random_state=42)
        val_df, test_df = train_test_split(val_df, test_size=0.5, random_state=42)
        return train_df, val_df, test_df


    def prepare(self):
        """ Prepares data with train-val-test split.

        Returns
        --------
        None - Will write splits to data directory
        """
        df = self.encode_labels()
        train_df, val_df, test_df = self.split_dataset(df)

        self.write_parquet(np.array_split(train_df, 100), 'traindata.parquet')
        self.write_parquet(np.array_split(val_df, 100), 'valdata.parquet')
        self.write_parquet(np.array_split(test_df, 100), 'testdata.parquet')



    def embedding(self, df, train=False):
        """ Creates embedding matrix for text. Must have 'text' and 'level_labels'
            column.

        Parameters
        -----------
        df: pd.Dataframe
            Pandas dataframe with shape (m x n). m is number of articles.

        Returns
        -----------
        embedding_matrix: np.array
            Numpy array with dimensions (m x d). m is number of articles and d
            is embedding dimensions.
        labels: pd.Series
            Series with dimensions (m x 1).
        """
        if train == True:
            df.dropna(subset=['text'], inplace=True)
            embedding_matrix = self.vectorizer.fit(df['text'])
            return
        embedding_matrix = self.vectorizer.transform(df['text'])
        labels = df[f'{self.level}_labels']
        return embedding_matrix, labels
