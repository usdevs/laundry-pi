"""
    Intended use in cron file: git pull [blahblah] && git log --pretty=oneline -1 | python scripts/flagger.py
    Sets a flag to trigger termination of main.py.
"""

import sys
from pathlib import Path

cwd = Path(__file__).parent
cache = cwd / 'lastcommit'
flag = cwd / 'flag'

def main():
    args = sys.stdin.read()
    curr_code, *message = args.split()

    with cache.open('r') as f:
        prev_code = f.readline()

    if curr_code == prev_code:
        print('no new commits')
        return

    print('replaced prev with curr')
    print('prev:', prev_code)
    print('curr:', curr_code)
    flag.touch()
    with cache.open('w') as f:
        f.write(curr_code)

if __name__ == '__main__':
    main()
