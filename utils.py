import datetime as dt
import logging
import sys
import os

## Date time
SG_TIMEZONE = dt.timezone(dt.timedelta(hours=8),'SGT') # dt.tzinfo object representing Singapore Time

def sg_time_now():
    """Get the current date time, with the time zone set to Singapore time (GMT +8)."""
    return dt.datetime.now(SG_TIMEZONE)

def to_py_time(googletime):
    """Converts the datetime returned by firestore library to a Python datetime."""
    return dt.datetime(googletime.year, googletime.month, googletime.day,
                                googletime.hour, googletime.minute, googletime.second,
                                googletime.microsecond, googletime.tzinfo)

## Logging
def init_logger(logdir="", logger_name=None):
    """Configures logger to log all DEBUG and above logs to the file all.log and to log all INFO and
    above to info.log. Also configures logger to log any uncaught exceptions (in addition to
    printing them to the console).

    Args:
        logdir (str or pathlib.Path, optional): Directory to save log files in. Defaults to "".
            "" will save to the current directory (where the script is run from).
        logger_name (str or None, optional): Name of logger to configure. Defaults to None.
            None will get the root logger.
    """
    log = logging.getLogger(logger_name)
    log.setLevel(logging.DEBUG)

    # Logging format
    fmt = logging.Formatter("[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d:%(funcName)s]"
                            " %(message)s")

    # Configure files to log to
    all = logging.FileHandler(os.path.join(logdir, 'all.log'))
    all.setLevel(logging.DEBUG)
    all.setFormatter(fmt)
    log.addHandler(all)

    info = logging.FileHandler(os.path.join(logdir, 'info.log'))
    info.setLevel(logging.INFO)
    info.setFormatter(fmt)
    log.addHandler(info)

    # Log any uncaught exceptions
    old_excepthook = sys.excepthook # prints to console
    def new_excepthook(type, value, tb):
        log.error("Uncaught exception: " + str(value), exc_info = (type, value, tb))
        old_excepthook(type, value, tb)

    sys.excepthook = new_excepthook
