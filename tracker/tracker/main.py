import argparse
from .maoyan import fetch as maoyan_fetch
from .line_protocol import parse
from .japan import fetch as japan_fetch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maoyan', action='store_true')
    parser.add_argument('--japan', action='store_true')

    args = parser.parse_args()
    if args.maoyan:
        data = maoyan_fetch()
        print(parse(data))
    if args.japan:
        data = japan_fetch()
        print(parse(data))
