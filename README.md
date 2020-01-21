# Laundry Pi
Laundry machine availability for Cinnamon College.

This is the code that lives on the Raspberry Pi:

The main script, main.py, checks whether the indicator light on each machine
is on, and updates Firestore. Device specific configuration is in config.py -
an example file (config.py.example) is uploaded.

In addition, there is a system (flagger.py, runner.py) to help restart the code
on the RPi each time a new commit on master branch in Github is made (checks
every minute). **Do not rebase/modify commits in master, it will break this
system** (probably can be fixed by changing the `git pull` command run on the
RPi to `git pull --force`?)

## Reading the log files

main.py will write log files to the directory specified in config.py. Our
current convention for the log directory is `~/laundro_logs/<pi ID>/`.

A log file can be read with live updates using:
```
tail -f <name of log file>
```

`all.log` contains all log messages, `info.log` contains only INFO level and
above log messages. Practically speaking, log messages for individual sensor
readings will be in `all.log` and not `info.log`.

## Setup

### 1. Install dependencies 
`pip install` :
- firebase-admin
- Adafruit-Blinka
- Adafruit-ADS1x15

### 2. Setup device specific configuration in config.py
1. Generate another firestore cert, and save it somewhere on the RPi
2. Copy `config.py.example` as `config.py` and fill in it in appropriately.
    `FIRESTORE_CERT` refers to the path to the firestore cert file we generated
    above.

### 3. Add tasks to crontab
`crontab -e` then add:
- `@reboot cd path/to/laundro && python3 runner.py main.py main` (start the main
  script when the RPi boots up)
- `* * * * * cd path/to/laundro && git pull && git log --pretty=oneline -1 |
  python3 flagger.py` (check Github for updates every minute)

## FYI: How things work

### System to update from Github: flagger.py and runner.py
This is a small ecosystem to reload the code on the pi each time a new commit is
made.

I can't quite figure out how to robustly do dynamic imports . ^ .

This means runner.py currently only works when it is in the same parent
directory as the main routine.

#### flagger.py
This script receives a version identifier through stdin and compares it to
`.lastcommit`. If there are differences (i.e. a change has been made),
`.lastcommit` is updated and a `.flag` is set.

`.lastcommit` and `.flag` are always in the same directory as `flagger.py`

The intended usage is: `git pull && git log --pretty=oneline -1 | python3
flagger.py`

#### runner.py [module path] [function]
This script loads a module with the python import path `module path` and runs
`function` in a process. Upon the process terminating, `module path` is reloaded
and the new `function` is run in a new process.

The intended usage is: `python3 runner.py main.py main`

For testing: `python3 runner.py runner test` (.py isn't necessary in module
path)

#### Requirements for main routine (currently main.py)
The main routine should regularly check for `.flag` and terminate once it is set
(it should also remove the flag). When this happens runner.py will restart the
main routine so it is running the updated code. flagger.py contains a simple
flag class that can be used.

### Firestore database

**About Firestore**: Firestore is an unstructured database. It can have
collections, which can contain other collections and documents. A document is
basically a database record. Each document has a unique string ID, which is what
you see in the sidebar on the Firestore webpage. Documents in the same
collection need not have the same fields (same "structure"), as you would in a
relational database, but we try to do so in this project to make life easier.

**The laundro database** has 3 collections: laundry_status, pi_status and
laundry_status_history.

#### pi_status
This keeps track of the information about each RPi (potentially other devices in
the future), namely:

1. piNo (number): a unique number to identify this RPi.
2. level (number): the floor the RPi is on.
3. lastSeen (timestamp): when the RPi was last seen. This is updated whenever
   any of the machines change status, or after 5 minutes, whichever it sooner.

#### laundry_status
This keeps track of the current status for each washer/dryer. The document ID is
unique to each washer/dryer in Cinnamon. Each document has the following fields:

1. *pinNo (number): unique number to identify each laundry machine in Cinnamon.
_I might change this to a more descriptive string in the future (eg. lvl17-1)_
2. *piNo (number): the RPi this laundry machine's sensor is connected to.
3. *on (boolean): is the laundry machine on?
4. *timeChanged (timestamp): when the laundry machine changed from on->off or
   vice versa.
5. *timeChangedCertain (boolean): is the start time for the washing/drying cycle
   accurate?
6. *washer (boolean): is this a washing machine?
7. name (string): name that Cinnabot displays.
8. ezlink (boolean): does this machine use ezlink card payment?
9. cinnabot (boolean): should Cinnabot display this machine?

\*: These fields are needed for the code here, the rest are not and used for the
frontend (Cinnabot) instead. (not the best database design but it's easier to
view and saves Firestore reads)

#### laundry_status_history
This is a backup of all the changes to the laundry machine status, whenever a
machine changes from on to off / vice versa.

