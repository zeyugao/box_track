import argparse
from .maoyan import fetch as maoyan_fetch
from .line_protocol import parse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maoyan', action='store_true')

    args = parser.parse_args()
    if args.maoyan:
        data = maoyan_fetch()
        print(parse(data))
