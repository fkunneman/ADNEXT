# standard lib:
from glob import glob
import random as rnd
from collections import namedtuple

# sklearn:
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.preprocessing import LabelEncoder

# pattern:
from pattern.db import Datasheet


def load_data(random_state=1066, filename="dummy.csv", max_n=10000):
    """
    Will load the data from the standard data .csv-format.
    Expects UTF-8 encoding.
    """

    # initialize the dataset
    fields = "user_id age gender loc_country loc_region loc_city education pers_big5 pers_mbti texts".split()
    dataset = {k:[] for k in fields}

    # shuffle the dataset:
    rnd.seed(random_state)
    rows = Datasheet.load(filename)
    rnd.shuffle(rows)

    for row in rows:
        # apply cutoff
        if max_n <= 0:
            break
        # update cnt:
        max_n -= 1
        # extract row:
        for category, val in zip(fields, row):
            dataset[category].append(val)

    return dataset


def split_train_dev_test(X, y, dev_prop=0.10, test_prop=0.20):

    enc = LabelEncoder()
    y = enc.fit_transform(classe)

    # split train and test
    train_idx, test_idx = StratifiedShuffleSplit(y, n_iter=1, test_size=test_prop,
                                                 random_state=RANDOM_STATE)[0]
    train_X = [X[i] for i in train_idx]
    train_y = [y[i] for i in train_idx]

    test_X = [X[i] for i in test_idx]
    test_y = [y[i] for i in test_idx]

    # split train and dev
    train_idx, dev_idx = StratifiedShuffleSplit(train_y, n_iter=1, test_size=dev_prop,
                                                 random_state=RANDOM_STATE)[0]
    train_X = [X[i] for i in train_idx]
    train_y = [y[i] for i in train_idx]

    dev_X = [X[i] for i in dev_idx]
    dev_y = [y[i] for i in dev_idx]

    return train_X, train_y, dev_X, dev_y, test_X, test_y, label_encoder


"""
E.g.
dataset = load_data(filename="../data/blogger_nl_merged.csv", random_state=1066, max_n=500)

texts = dataset['texts']
gender_label = dataset['gender']

train_X, train_y, dev_X, dev_y, test_X, test_y, label_encoder = \
                            split_train_dev_test(texts, gender_label,
                                dev_prop=0.20, test_prop=0.15)
"""
