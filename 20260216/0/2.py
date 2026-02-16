#!/usr/bin/share python3

import sys
from pathlib import Path

for p in Path(sys.argv[1], '.git/objects').glob('**/*'):
    if p.is_file() and p.parent.name not in ('info', 'pack'):
        print(p.parent.name + p.name)