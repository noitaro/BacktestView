import ccxt
import pandas as pd
from datetime import datetime
import calendar

from_datetime = datetime(year=2021, month=11, day=1, hour=0, minute=0, second=0, microsecond=0)
to_datetime = datetime(year=2021, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)

from_timestamp = calendar.timegm(from_datetime.utctimetuple())*1000
to_timestamp = calendar.timegm(to_datetime.utctimetuple())*1000

tmp_timestamp = from_timestamp
ohlcv_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
bybit = ccxt.bybit()

while True:
    fetch_ohlcv = bybit.fetch_ohlcv(symbol='BTC/USD', timeframe='1h', since=tmp_timestamp)
    df = pd.DataFrame(fetch_ohlcv, columns=ohlcv_df.columns)
    ohlcv_df = ohlcv_df.append(df, ignore_index=True)

    start_datetime = datetime.fromtimestamp(int(df.iloc[0].at['timestamp'])/1000)
    end_datetime = datetime.fromtimestamp(int(df.iloc[-1].at['timestamp'])/1000)
    # データが取れなかった場合、終了
    if start_datetime == end_datetime:
        break

    print(f'CCXT: START={start_datetime}, END={end_datetime}')
    tmp_timestamp = int(end_datetime.timestamp()*1000)
    
    # 終了データまで取得した場合、終了
    if tmp_timestamp >= to_timestamp:
        break
    pass

# 重複行削除
# fetch_ohlcvの切れ目が重複するため
ohlcv_df.drop_duplicates(inplace=True)

# ソート
ohlcv_df.sort_values('timestamp', ascending=True, inplace=True, ignore_index=True)

# 多い分を削除
# fetch_ohlcvで多めに取れているため
ohlcv_df = ohlcv_df[ohlcv_df['timestamp'] <= to_timestamp]

print(ohlcv_df)