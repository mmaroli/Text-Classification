from utilities.dataloader import DataLoader, XGBoostLoader
from classifiers.neural_classifier import Neural


if __name__ == '__main__':
    classifier = Neural(level='subsubcat', epochs=5)

    classifier.prepare_training_data()
