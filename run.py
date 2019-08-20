from utilities.dataloader import DataLoader, XGBoostLoader
from classifiers.xgboost_classifier import XGBoostClassifier


if __name__ == '__main__':
    classifier = XGBoostClassifier(level='cat', epochs=5)

    # classifier.prepare_training_data()
    classifier.fit_tfidf()
    classifier.train()
