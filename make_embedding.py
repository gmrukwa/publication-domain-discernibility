import argparse
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True,
                        help='data source')
    parser.add_argument('--categories', required=True,
                        help='categories source')
    parser.add_argument('--embedding', required=True,
                        help='embedding destination')
    parser.add_argument('--words', required=True,
                        help='words destination')
    parser.add_argument('--N', default=5, type=int,
                        help='number of characteristic words')
    parser.add_argument('--max-features', default=100000, type=int,
                        help='the number of embedding features')
    parser.add_argument('--ngram-length', default=3, type=int,
                        help='the maximal length of n-gram')
    return parser.parse_args()


def load_pickle(fname):
    with open(fname, 'rb') as infile:
        return joblib.load(infile)


def save_pickle(data, fname):
    with open(fname, 'wb') as outfile:
        joblib.dump(data, outfile)


def load_json(fname):
    with open(fname) as infile:
        return json.load(infile)


def save_json(obj, fname):
    with open(fname, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=2)


def select_categories(data, categories):
    selection = np.zeros((data.shape[0],), dtype=bool)
    for category in categories:
        selection = np.logical_or(selection, data.domain == category)
    return data[selection].copy()


def effect_size(first, second, axis=0):
    mu1 = first.mean(axis=axis)
    mu2 = second.mean(axis=axis)
    s1 = np.var(first, axis=axis)
    s2 = np.var(second, axis=axis)
    n1, n2 = first.shape[axis], second.shape[axis]
    s = np.sqrt((n1 * s1 + n2 * s2) / (n1 + n2 - 2))
    d = mu1 - mu2 / s
    return d


def characteristic_features(data, selector, n: int=5):
    first = data[selector, :].toarray()
    second = data[selector == 0, :].toarray()
    d = effect_size(first, second)
    d_sort = np.argsort(d)
    top = d_sort[-n::-1]
    bot = d_sort[:n]
    return bot, top


def main():
    args = parse_args()
    data = load_pickle(args.source)
    categories = load_json(args.categories)
    data = select_categories(data, categories)
    vectorizer = TfidfVectorizer(ngram_range=(1,args.ngram_length),
                                 max_features=args.max_features)
    embedding = vectorizer.fit_transform(data.clean)
    save_pickle(embedding, args.embedding)
    words = vectorizer.get_feature_names()
    characteristic_words = {}
    for domain in tqdm(categories):
        category = (data.domain == domain).ravel()
        bot, top = characteristic_features(
            embedding, category, n=args.N)
        characteristic_words[f'{domain}_up'] = words[top]
        characteristic_words[f'{domain}_down'] = words[bot]
    save_json(characteristic_words, args.words)


if __name__ == '__main__':
    main()
