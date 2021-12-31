from datetime import datetime
import calendar
from dateutil.tz import tzlocal

def dateToTimestamp(date: str, hour: int, minute: int, second: int):
    '''
    1609459200000 <- '2021-01-01'
    '''
    localtimezone = tzlocal()
    date_ymd = date.split('-')
    now = datetime(int(date_ymd[0]), int(date_ymd[1]), int(date_ymd[2]), hour=hour, minute=minute, second=second, microsecond=0, tzinfo=localtimezone)
    unixtime = calendar.timegm(now.utctimetuple())
    timestamp = unixtime * 1000

    print(f"datetime: {str_format_datetime(now)}, timestamp: {timestamp}")
    return timestamp

def datetimeToTimestamp(dt: datetime):
    '''
    1609459200000 <- 2021-01-01 09:00:00
    '''
    localtimezone = tzlocal()
    now = datetime(dt.year, dt.month, dt.day, hour=dt.hour, minute=dt.minute, second=dt.second, microsecond=0, tzinfo=localtimezone)
    unixtime = calendar.timegm(now.utctimetuple())
    timestamp = unixtime * 1000

    print(f"datetime: {str_format_datetime(now)}, timestamp: {timestamp}")
    return timestamp

def timestampToDatetime(timestamp: str):
    '''
    2021-01-01 09:00:00 <- 1609459200000
    '''
    return datetime.fromtimestamp(int(timestamp)/1000)

def str_format_datetime(dt: datetime):
    '''
    '2021/12/20 21:00:00' <- '1640001600000'
    '''
    return dt.strftime("%Y/%m/%d %H:%M:%S")