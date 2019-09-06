import time
from pathlib import Path

# DUMMY COMMIT

class FileExistsFlag:
    def __init__(self, path):
        self.path = Path(path)

    def flag(self):
        try:
            self.path.touch()
        except FileExistsError:
            pass # already flagged

    def unflag(self):
        self.path.unlink()

    def flagged(self):
        return self.path.exists()

def main():
    flag = FileExistsFlag('./flag')
    t = 0
    while not flag.flagged():
        t += 1
        time.sleep(1)
        print(f'waiting for flag for {t} seconds')
    flag.unflag()
