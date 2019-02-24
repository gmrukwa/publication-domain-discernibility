import argparse
import json
import os

from discover import interpret, evaluate


_DEFAULT_DESTINATION = os.path.join('data', 'pubs')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', required=True,
                        help='API Key for Microsoft Academic Search API')
    parser.add_argument('--config', default='config.json',
                        help='Configuration file')
    parser.add_argument('--destination', default=_DEFAULT_DESTINATION,
                        help='Destination of fetched publications')
    parser.add_argument('--count', default=1000, type=int,
                        help='Number of publications to discover per domain')
    return parser.parse_args()


def load_json(path: str):
    with open(path) as infile:
        return json.load(infile)


def save_json(path: str, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def main():
    args = parse_args()
    config = load_json(args.config)
    os.makedirs(args.destination)
    destination_pattern = os.path.join(args.destination, "{0}.json")
    for domain in config["DOMAINS"]:
        query = interpret.fetch_query(domain, config["API"], args.api_key)
        papers = evaluate.request_papers(query, config["API"], args.api_key,
                                         count=args.count)
        save_json(destination_pattern.format(domain), papers)


if __name__ == '__main__':
    main()
