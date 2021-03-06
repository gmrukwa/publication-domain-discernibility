import argparse
import glob
import json
import os
import requests

from tqdm import tqdm

from utils import DEFAULT_DESTINATION, load_json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=DEFAULT_DESTINATION,
                        help='Source directory of domain articles lists')
    parser.add_argument('--count', default=1000, type=int,
                        help='Limits the number of downloaded papers')
    parser.add_argument('--force', action='store_const', const=True,
                        default=False, help='Force re-download')
    return parser.parse_args()


def is_downloadable(url: str):
    try:
        h = requests.head(url, allow_redirects=True)
    except requests.exceptions.RequestException:
        return False
    header = h.headers
    content_type = header.get('content-type')
    if content_type is None:
        return False
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def download(url: str, destination: str, skip_existing: bool = True):
    if skip_existing and os.path.exists(destination):
        return
    request = requests.get(url, allow_redirects=True)
    with open(destination, 'wb') as outfile:
        outfile.write(request.content)


def find_domain_lists(source: str):
    return glob.glob(os.path.join(source, '*.json'))


def domain_dir(domain_list_fname: str):
    return os.path.splitext(domain_list_fname)[0]


_PDF_TYPE = 3


def as_downloadable(publication):
    title = publication["Ti"]
    meta = json.loads(publication["E"])
    sources = meta.get("S", [])
    for source in sources:
        if source["Ty"] == _PDF_TYPE and is_downloadable(source["U"]):
            return title, source["U"]
    return title, ""


def as_download_list(pubs, limit: int):
    parsed = (as_downloadable(pub) for pub in pubs)
    downloadable = ((title, url) for title, url in parsed if url)
    return (pub for pub, _ in zip(downloadable, range(limit)))


def main():
    args = parse_args()
    domain_lists = find_domain_lists(args.source)
    for domain in tqdm(domain_lists, 'domain'):
        os.makedirs(domain_dir(domain), exist_ok=True)
        pattern = os.path.join(domain_dir(domain), '{0}.pdf')
        allowed_title_len = 255 - len(pattern) + 3
        pubs = load_json(domain)
        queue = as_download_list(pubs["entities"], args.count)
        for title, url in tqdm(queue, 'publication', total=args.count):
            filename = pattern.format(title[:min(len(title), allowed_title_len)])
            download(url, filename, not args.force)


if __name__ == '__main__':
    main()
