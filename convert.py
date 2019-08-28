import argparse
from functools import partial
import glob
import logging
from multiprocessing import Pool
import os
import subprocess

from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True,
                        help='Source directory with publication PDFs')
    parser.add_argument('--destination', required=True,
                        help='Destination directory for publication TXTs')
    return parser.parse_args()


def convert_pdf(src: str, dst: str):
    completed = subprocess.run(['pdf2txt.py', '-o', dst, src])
    if completed.returncode:
        logging.warning(f"{src} conversion failed.")


def prepare_destination(src: str, dst_root: str):
    head, fname = os.path.split(src)
    _, category = os.path.split(head)
    pub_name, _ = os.path.splitext(fname)
    dst_dir = os.path.join(dst_root, category)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, f"{pub_name}.txt")
    return dst


def convert(src: str, dst_root: str):
    dst = prepare_destination(src, dst_root)
    convert_pdf(src, dst)


def main():
    args = parse_args()
    pattern = os.path.join(args.source, '**', '*.pdf')
    queue = glob.glob(pattern, recursive=True)
    _convert = partial(convert, dst_root=args.destination)
    with Pool(20) as pool:
        pool.map(_convert, tqdm(queue, 'conversion'))


if __name__ == '__main__':
    main()
