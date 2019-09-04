import pandas as pd
import pytest

import clean


@pytest.fixture
def pubs():
    return pd.DataFrame(data={
        'publications': [
            'aaaaaa',
            'a a a',
            'to by blah',
            'http://blah.com to by blah word',
            'some proper long publication that should be passed',
            'gev vt vk Ek 1MW'
        ],
        'domain': 6 * ['some_domain']
    })


def test_clean_e2e(pubs):
    df = clean.clean(pubs, min_chars=6, min_words=3)
    assert df.shape[0] == 4
