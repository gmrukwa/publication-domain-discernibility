import argparse
import os

from discover import interpret, evaluate
from utils import load_json, save_json, DEFAULT_DESTINATION


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', required=True,
                        help='API Key for Microsoft Academic Search API')
    parser.add_argument('--config', default='config.json',
                        help='Configuration file')
    parser.add_argument('--destination', default=DEFAULT_DESTINATION,
                        help='Destination of fetched publications')
    parser.add_argument('--count', default=1000, type=int,
                        help='Number of publications to discover per domain')
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_json(args.config)
    os.makedirs(args.destination, exist_ok=True)
    destination_pattern = os.path.join(args.destination, "{0}.json")
    for domain in config["DOMAINS"]:
        query = interpret.fetch_query(domain, config["API"], args.api_key)
        papers = evaluate.request_papers(query, config["API"], args.api_key,
                                         count=args.count)
        save_json(destination_pattern.format(domain), papers)


if __name__ == '__main__':
    main()
