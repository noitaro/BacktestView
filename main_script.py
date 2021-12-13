import eel # pip install eel
import ccxt
import asyncio
import pandas_ta as ta  # pip install -U git+https://github.com/twopirllc/pandas-ta
import pandas as pd  # pip install pandas
import sub_script as utility

# python -m eel main_script.py web --onefile --noconsole --icon=Icojam-Animals-01-horse.ico


async def main():

    eel.init('web')
    eel.start('index.html', port=0, size=(1200, 800))

    pass


@eel.expose
def get_ohlcv(from_date: str, to_date: str):
    if from_date is None or to_date is None:
        return None

    # 1609459200000 <- '2021-01-01'
    from_timestamp = utility.dateToTimestamp(from_date)
    to_timestamp = utility.dateToTimestamp(to_date)
    print(f'OHLCV取得: FROM={from_date}, TO={to_date}')

    ohlcv_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    bybit = ccxt.bybit()
    tmp_timestamp = from_timestamp
    while True:
        tmp_ohlcv = bybit.fetch_ohlcv(symbol='BTC/USD', timeframe='1h', since=tmp_timestamp)
        tmp_df = pd.DataFrame(tmp_ohlcv, columns=ohlcv_df.columns)
        ohlcv_df = ohlcv_df.append(tmp_df, ignore_index=True)

        start_datetime = utility.timestampToDatetime(tmp_df.iloc[0].at['timestamp'])
        end_datetime = utility.timestampToDatetime(tmp_df.iloc[-1].at['timestamp'])
        # データが取れなかった場合、終了
        if start_datetime == end_datetime:
            break

        print(f'CCXT: START={start_datetime}, END={end_datetime}')
        tmp_timestamp = int(end_datetime.timestamp() * 1000)
        
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

    return ohlcv_df.to_json()


@eel.expose
def get_vwma(timestamp, close, volume, length):
    df = pd.DataFrame()
    df['timestamp'] = pd.DataFrame.from_dict(timestamp, orient='index')
    df['close'] = pd.DataFrame.from_dict(close, orient='index')
    df['volume'] = pd.DataFrame.from_dict(volume, orient='index')
    df['vwma'] = ta.vwma(df['close'], df['volume'], length)
    return df.loc[:,['timestamp', 'vwma']].to_json()


@eel.expose
def get_cci(timestamp, high, low, close, length):
    df = pd.DataFrame()
    df['timestamp'] = pd.DataFrame.from_dict(timestamp, orient='index')
    df['high'] = pd.DataFrame.from_dict(high, orient='index')
    df['low'] = pd.DataFrame.from_dict(low, orient='index')
    df['close'] = pd.DataFrame.from_dict(close, orient='index')
    df['cci'] = ta.cci(df['high'], df['low'], df['close'], length)
    return df.loc[:,['timestamp', 'cci']].to_json()



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception:
        pass
