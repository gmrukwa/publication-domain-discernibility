import argparse
import glob
import os

import pdftotext
from tqdm import tqdm

from utils import DEFAULT_DESTINATION


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=DEFAULT_DESTINATION,
                        help='Source directory with publication PDFs')
    return parser.parse_args()


def convert(path: str):
    with open(path, 'rb') as infile:
        pdf = pdftotext.PDF(infile)
    out_path = "{0}.txt".format(os.path.splitext(path)[0])
    with open(out_path, 'w') as outfile:
        for i in range(len(pdf)):
            normalized = pdf[i].encode('ascii', errors='replace').decode('ascii')
            outfile.write(normalized)


def main():
    args = parse_args()
    pattern = os.path.join(args.source, '**', '*.pdf')
    queue = glob.glob(pattern, recursive=True)
    for path in tqdm(queue, 'conversion'):
        convert(path)


if __name__ == '__main__':
    main()
