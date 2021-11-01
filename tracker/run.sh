#!/bin/bash

pushd $(dirname $0) >& /dev/null
python3 -m tracker --maoyan
