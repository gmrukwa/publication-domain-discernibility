from functools import partial
import glob
import os
import re

import nltk
import pandas as pd
import joblib
from tqdm import tqdm


def read_txt(fname: str):
    with open(fname) as infile:
        return infile.read()


def read_pubs(dir:str, ext: str = 'txt'):
    fnames = glob.glob(os.path.join(dir, '.'.join(['*', ext])))
    return [read_txt(fname) for fname in tqdm(fnames, desc='file', leave=False)]


def get_subdirs(dir: str):
    return [
        name for name in glob.glob(os.path.join(dir, '*'))
        if os.path.isdir(name)
    ]


def as_df(pub_list, sub: str):
    domain = os.path.split(sub)[-1]
    return pd.DataFrame(data={
        "publications": pub_list,
        "domain": len(pub_list)*[domain]
    })


def read_all(dir: str, ext: str = 'txt'):
    subdirs = get_subdirs(dir)
    pubs = [read_pubs(sub, ext=ext) for sub in tqdm(subdirs, desc='directory')]
    frames = [as_df(pub_list, sub) for pub_list, sub in zip(pubs, subdirs)]
    return pd.concat(frames).reset_index(drop=True)


def is_short_text(pub: str, min_chars: int=5000, min_words: int=1500):
    return len(pub) < min_chars or len(pub.split()) < min_words


non_alphabet = re.compile('[^a-zA-Z ]')


def remove_nonalphabet(word):
    return non_alphabet.sub('', word)


english_stopwords = set(nltk.corpus.stopwords.words('english'))


def remove_stopwords(word):
    return word if word not in english_stopwords else ''


stemmer = nltk.stem.snowball.EnglishStemmer()


def extract_stem(word):
    return stemmer.stem(word)


lemmatizer = nltk.stem.WordNetLemmatizer()


def lemmatize(word):
    return lemmatizer.lemmatize(word)


def remove_short_words(word, min_len: int=4):
    return word if len(word) >= min_len else ''


url = re.compile(r"([a-z]([a-z]|\d|\+|-|\.)*):(\/\/(((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?((\[(|(v[\da-f]{1,}\.(([a-z]|\d|-|\.|_|~)|[!\$&'\(\)\*\+,;=]|:)+))\])|((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=])*)(:\d*)?)(\/(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*|(\/((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)|((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)|((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)){0})(\?((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\xE000-\xF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?")


def remove_url(word, naive: bool=True):
    if word.startswith('http'):
        if naive:
            return ''
        return url.sub('', word)
    return word


def _iter(func, lazy: bool=False, verbose: bool=False):
    if lazy:
        return partial(map, func)
    if verbose:
        def vectorized(row):
            return [func(word) for word in tqdm(row, desc='row', leave=False)]
    else:
        def vectorized(row):
            return [func(word) for word in row]
    return vectorized


def remove_empty(row):
    return [word for word in row if word]


def initialize_pandas_progress():
    from pandas.core.frame import DataFrame
    from pandas.core.series import Series
    from pandas.core.window import _Rolling_and_Expanding
    def inner_generator(df_function='apply'):
        def inner(df, func, **kwargs):
            # Precompute total iterations
            if df_function == 'applymap':
                total = df.size
            elif isinstance(df, Series):
                total = len(df)
            elif _Rolling_and_Expanding is None or \
                    not isinstance(df, _Rolling_and_Expanding):
                # DataFrame or Panel
                axis = kwargs.get('axis', 0)
                if axis == 'index':
                    axis = 0
                elif axis == 'columns':
                    axis = 1
                # when axis=0, total is shape[axis1]
                total = df.size // df.shape[axis]

            # Init bar
            t = tqdm(total=total, desc=kwargs.pop('desc', None))

            # Define bar updating wrapper
            def wrapper(*args, **kwargs):
                # update tbar correctly
                # it seems `pandas apply` calls `func` twice
                # on the first column/row to decide whether it can
                # take a fast or slow code path; so stop when t.total==t.n
                t.update(n=1 if not t.total or t.n < t.total else 0)
                return func(*args, **kwargs)

            # Apply the provided function (in **kwargs)
            # on the df using our wrapper (which provides bar updating)
            result = getattr(df, df_function)(wrapper, **kwargs)

            # Close bar and return pandas calculation result
            t.close()
            return result

        return inner
    Series.progress_apply_d = inner_generator()
    Series.progress_map_d = inner_generator('map')
    DataFrame.progress_apply_d = inner_generator()
    DataFrame.progress_applymap_d = inner_generator('applymap')



def clean(pubs, min_chars: int=5000, min_words: int=1500,
          min_word_len: int=4, lazy: bool=False):
    _v = partial(_iter, lazy=lazy)
    _is_short_text = partial(is_short_text, min_chars=min_chars,
                             min_words=min_words)
    _remove_short_words = partial(remove_short_words, min_len=min_word_len)
    long_enough = pubs[~pubs.publications.apply(_is_short_text)].copy()
    initialize_pandas_progress()
    long_enough['clean'] = long_enough.publications\
        .progress_apply_d(str.strip, desc='strip')\
        .progress_apply_d(str.lower, desc='lower')\
        .progress_apply_d(str.split, desc='split')\
        .progress_apply_d(_v(_remove_short_words), desc='remove short')\
        .progress_apply_d(_v(remove_url), desc='remove url')\
        .progress_apply_d(_v(remove_nonalphabet), desc='remove nonalphabet')\
        .progress_apply_d(_v(remove_stopwords), desc='remove stopwords')\
        .progress_apply_d(_v(lemmatize), desc='lemmatize')\
        .progress_apply_d(_v(_remove_short_words), desc='remove short')\
        .progress_apply_d(_v(str.strip), desc='strip')\
        .progress_apply_d(remove_empty, desc='remove empty')\
        .progress_apply_d(' '.join, desc='join')
    return long_enough


def main():
    pubs = read_all(os.path.join('data', 'pubs'))
    pubs = clean(pubs, lazy=False)
    with open(os.path.join('data', 'pubs-clean.pkl'), 'wb') as outfile:
        joblib.dump(pubs, outfile)


if __name__ == '__main__':
    main()
