import argparse
from .maoyan import fetch as maoyan_fetch

parser = argparse.ArgumentParser()
parser.add_argument('--maoyan', action='store_true')

args = parser.parse_args()
print(args)
if args.maoyan:
    maoyan_fetch()
