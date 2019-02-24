import requests


def _build_query(domain_name, config):
    str_value = '"{0}"'.format
    make_param = '='.join
    chain_params = '&'.join
    query = chain_params([
        make_param(["query", str_value(domain_name)]),
        make_param(["complete", int(config["AUTOCOMPLETE_MODE"])]),
        make_param(["count", 1]),
        make_param(["offset", 0]),
        make_param(["timeout", config["TIMEOUT"]]),
        make_param(["model", str_value(config["MODEL_NAME"])])
    ])
    return query


def build_headers(key):
    return {
        "content-type": "application/x-www-form-urlencoded",
        "ocp-apim-subscription-key": key
    }


def _request_domain_interpretations(domain_name, config, key):
    request = requests.post(config["INTERPRET_URL"],
                            data=_build_query(domain_name, config),
                            headers=build_headers(key))
    if not request.ok():
        raise RuntimeError('Domain {0} could not be parsed.'.format(domain_name))

    return request.json()


def _parse_domain_query(response):
    # Should work for simple queries
    return response["interpretations"][0]["rules"][0]["output"]["value"]


def fetch_query(domain_name, config, key):
    response = _request_domain_interpretations(domain_name, config, key)
    interpretation = _parse_domain_query(response)
    return interpretation
