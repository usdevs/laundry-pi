import sys
from pathlib import Path

class Flag:
    def __init__(self, path):
        self.path = Path(path)

    def __bool__(self):
        return self.flagged()

    def flagged(self):
        return self.path.is_file()

    def set(self):
        try:
            self.path.touch()
        except:
            pass # flag already set

    def unflag(self):
        self.path.unlink()

cwd = Path(__file__).parent
cache = cwd / '.lastcommit'
flag = cwd / '.flag'

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
