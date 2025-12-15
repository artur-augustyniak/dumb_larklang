#!/usr/bin/env python3
import sys
from dumblang import parse_and_execute

if __name__ == "__main__":
    src = open(sys.argv[1]).read()
    res = parse_and_execute(src)
    print(res)
