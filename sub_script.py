from datetime import datetime
import calendar

def dateToTimestamp(date: str):
    '''
    1609459200000 <- '2021-01-01'
    '''
    date_ymd = date.split('-')
    now = datetime(int(date_ymd[0]), int(date_ymd[1]), int(date_ymd[2]), hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    unixtime = calendar.timegm(now.utctimetuple())
    timestamp = unixtime * 1000

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