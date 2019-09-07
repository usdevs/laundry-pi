# Laundry Pi
Laundry machine availability for Cinnamon College

This is the code that lives on the Raspberry Pi

## Automatically update scripts!
This is a small ecosystem to reload the code on the pi each time a new commit is
made. It runs on 3 main components: flagger.py, runner.py and the main routine.

### `flagger.py`
This script receives a version identifier through stdin and compares it to
`.lastcommit`. If there are differences (i.e. a change has been made),
`.lastcommit` is updated and a `.flag` is set.

`.lastcommit` and `.flag` are always in the same directory as `flagger.py`

The intended usage is:
`git pull && git log --pretty=oneline -1 | python3 flagger.py`

### `runner.py [module path] [function]`
This script loads a module with the python import path `module path` and runs
`function` in a process. Upon the process terminating, `module path` is reloaded
and the new `function` is run in a new process.

The intended usage is: `python3 runner.py firebasePush.py main`

Also try: `python3 runner.py runner test` (.py isn't necessary in module path)

### Main routine
This can be any routine that frequently checks for `.flag` and terminates once
it is set (It should also unflag the flag). `flagger.py` contains a simple flag
class that can be used.

### Notes
I can't quite figure out how to robustly do dynamic imports . ^ .

runner.py currently only works when it is in the same parent directory as the
main routine.
