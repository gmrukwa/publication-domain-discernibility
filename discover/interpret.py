import requests

_QUERY_PATTERN = 'query="{0}"' \
                 '&complete={1}' \
                 '&count={2}' \
                 '&offset={3}' \
                 '&timeout={4}'\
                 '&model="{5}"'
_FIRST = 1
_NO_OFFSET = 0


def _build_query(domain_name, config):
    return _QUERY_PATTERN.format(domain_name,
                                 int(config["AUTOCOMPLETE_MODE"]),
                                 _FIRST,
                                 _NO_OFFSET,
                                 config["TIMEOUT"],
                                 config["MODEL_NAME"])


def build_headers(key):
    return {
        "content-type": "application/x-www-form-urlencoded",
        "ocp-apim-subscription-key": key
    }


def _request_domain_interpretations(domain_name, config, key):
    request = requests.post(config["INTERPRET_URL"],
                            data=_build_query(domain_name, config),
                            headers=build_headers(key))
    if not request.ok:
        raise RuntimeError('Domain {0} could not be parsed.'.format(domain_name))

    return request.json()


def _parse_domain_query(response):
    # Should work for simple queries
    return response["interpretations"][0]["rules"][0]["output"]["value"]


def fetch_query(domain_name, config, key):
    response = _request_domain_interpretations(domain_name, config, key)
    interpretation = _parse_domain_query(response)
    return interpretation
