from itertools import chain
import requests

from discover.interpret import build_headers


_QUERY_PATTERN = 'expr="{0}"' \
                 '&model="{1}"' \
                 '&count={2}' \
                 '&offset={3}' \
                 '&attributes={4}'
# according to: https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/evaluatemethod
# and: https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/paperentityattributes
_FIELDS = "Id,Ti,E,Y,AA.AuN"
_PAGINATION = 10


def _build_query(expression, config, count: int = 1000, offset: int = 0):
    return _QUERY_PATTERN.format(expression,
                                 config["MODEL_NAME"],
                                 count,
                                 offset,
                                 _FIELDS)


def request_papers(expression, config, key, count: int = 1000, offset: int = 0):
    request = requests.post(config["EVALUATE_URL"],
                            data=_build_query(expression, config, count, offset),
                            headers=build_headers(key))
    if not request.ok:
        raise RuntimeError(
            'Expression {0} could not be parsed.'.format(expression))

    response = request.json()

    if "aborted" in response and response["aborted"]:
        response = _scattered_request(expression, config, key, count)

    return response


def _chain_lists(iterable):
    return list(chain.from_iterable(iterable))


def _scattered_request(expression, config, key, count: int = 1000):
    step = count // _PAGINATION
    entities = _chain_lists(
        request_papers(expression, config, key, step, i * step)["entities"]
        for i in range(_PAGINATION)
    )
    response = {
        "expr": expression,
        "entities": entities
    }
    return response
