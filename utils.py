import datetime as dt

SG_TIMEZONE = dt.timezone(dt.timedelta(hours=8),'SGT') # dt.tzinfo object representing Singapore Time

def sg_time_now():
    return dt.datetime.now(SG_TIMEZONE)

def to_py_time(googletime):
    return dt.datetime(googletime.year, googletime.month, googletime.day,
                                googletime.hour, googletime.minute, googletime.second,
                                googletime.microsecond, googletime.tzinfo)
