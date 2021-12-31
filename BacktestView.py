import datetime
from typing import Dict
import eel # pip install eel
import ccxt # pip install ccxt
import asyncio
from gevent.greenlet import Greenlet
import pandas as pd
from pandas.core.frame import DataFrame  # pip install pandas
import pandas_ta as ta  # pip install -U git+https://github.com/twopirllc/pandas-ta
import sub_script as utility
import importlib
from decimal import Decimal
import os
import sys

# pip install PyInstaller
# python -m eel BacktestView.py web --onefile --noconsole --icon=Icojam-Animals-01-horse.ico

greenlet: Greenlet = None

async def main():
    print(__file__)

    eel.init('web')
    eel.start('index.html', port=0, size=(1200, 800))

    pass

def real_time_thread(exchange_name: str, symbol_name: str, timeframe: str, since_datetime: datetime):
    print(f'real_time_thread: EXCHANGE={exchange_name}, SYMBOL={symbol_name}, TIMEFRAME={timeframe}, DATETIME={utility.str_format_datetime(since_datetime)}')
    global is_real_time

    since_timestamp: int = utility.datetimeToTimestamp(since_datetime)
    tmp_timestamp: int = since_timestamp

    while is_real_time:
        print('real_time_thread: while')
        ohlcv_df = fetch_ohlcv(exchange_name, symbol_name, timeframe, tmp_timestamp, None)
        end_datetime = utility.timestampToDatetime(ohlcv_df.iloc[-1].at['timestamp'])
        tmp_timestamp = utility.datetimeToTimestamp(end_datetime)
        eel.sleep(5.0) # Use eel.sleep(), not time.sleep()


is_real_time = False
@eel.expose
def set_is_real_time(is_on: bool):
    global is_real_time

    print(f"is_real_time: {is_real_time}")
    is_real_time = is_on
    print(f"is_real_time: {is_real_time}")
    pass

@eel.expose
def get_ohlcv(exchange_name: str, symbol_name: str, timeframe: str, from_date: str, to_date: str):
    global greenlet
    if greenlet is not None:
        greenlet.kill()
        pass

    if exchange_name is None or exchange_name == '' or \
        symbol_name is None or symbol_name == '' or \
        timeframe is None or timeframe == '' or \
        from_date is None or from_date == '' or \
        to_date is None or to_date == '':
        return None

    print(f'get_ohlcv: EXCHANGE={exchange_name}, SYMBOL={symbol_name}, TIMEFRAME={timeframe}, FROM={from_date}, TO={to_date}')
    
    # 1609459200000 <- '2021-01-01'
    from_timestamp = utility.dateToTimestamp(from_date, 0, 0, 0)
    to_timestamp = utility.dateToTimestamp(to_date, 23, 59, 59)
    if from_timestamp >= to_timestamp:
        return None

    ohlcv_df = fetch_ohlcv(exchange_name, symbol_name, timeframe, from_timestamp, to_timestamp)
    end_datetime = utility.timestampToDatetime(ohlcv_df.iloc[-1].at['timestamp'])

    greenlet = eel.spawn(real_time_thread, exchange_name, symbol_name, timeframe, end_datetime)
    return ohlcv_df.to_json()

def fetch_ohlcv(exchange_name: str, symbol_name: str, timeframe: str, from_timestamp: int, to_timestamp: int = None):
    print(f'fetch_ohlcv: EXCHANGE={exchange_name}, SYMBOL={symbol_name}, TIMEFRAME={timeframe}, FROM={from_timestamp}, TO={to_timestamp}')
    
    ohlcv_df: DataFrame = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    exchange = eval('ccxt.' + exchange_name + '()')
    # exchange = ccxt.bybit()

    tmp_timestamp = from_timestamp
    while True:
        tmp_ohlcv = exchange.fetch_ohlcv(symbol=symbol_name, timeframe=timeframe, since=tmp_timestamp)
        tmp_df = pd.DataFrame(tmp_ohlcv, columns=ohlcv_df.columns)
        print(tmp_df)

        # 取得できない場合、終了
        if tmp_df.empty:
            break

        ohlcv_df = ohlcv_df.append(tmp_df, ignore_index=True)

        start_datetime = utility.timestampToDatetime(tmp_df.iloc[0].at['timestamp'])
        end_datetime = utility.timestampToDatetime(tmp_df.iloc[-1].at['timestamp'])
        # データが取れなかった場合、終了
        if start_datetime == end_datetime:
            break

        print(f'CCXT: START={start_datetime}, END={end_datetime}')
        tmp_timestamp = int(end_datetime.timestamp() * 1000)
        
        # 終了データまで取得した場合、終了
        if  to_timestamp is not None:
            if tmp_timestamp >= to_timestamp:
                break
        
        pass

    # 重複行削除
    # fetch_ohlcvの切れ目が重複するため
    ohlcv_df.drop_duplicates(inplace=True)

    # ソート
    ohlcv_df.sort_values('timestamp', ascending=True, inplace=True, ignore_index=True)

    # 多い分を削除
    if  to_timestamp is not None:
        # fetch_ohlcvで多めに取れているため
        ohlcv_df = ohlcv_df[ohlcv_df['timestamp'] <= to_timestamp]
        pass

    # timestamp -> datetime
    f_to_datetime = lambda x: utility.str_format_datetime(utility.timestampToDatetime(str(x)))
    ohlcv_df['datetime'] = ohlcv_df['timestamp'].map(f_to_datetime)

    return ohlcv_df

@eel.expose
def get_vwma(timestamp, close, volume, length):
    print(f'get_vwma: length={length}')
    df = pd.DataFrame()
    df['timestamp'] = pd.DataFrame.from_dict(timestamp, orient='index')
    df['close'] = pd.DataFrame.from_dict(close, orient='index')
    df['volume'] = pd.DataFrame.from_dict(volume, orient='index')
    df['vwma'] = ta.vwma(df['close'], df['volume'], length)
    return df.loc[:,['timestamp', 'vwma']].to_json()


@eel.expose
def get_cci(timestamp, high, low, close, length):
    print(f'get_cci: length={length}')
    df = pd.DataFrame()
    df['timestamp'] = pd.DataFrame.from_dict(timestamp, orient='index')
    df['high'] = pd.DataFrame.from_dict(high, orient='index')
    df['low'] = pd.DataFrame.from_dict(low, orient='index')
    df['close'] = pd.DataFrame.from_dict(close, orient='index')
    df['cci'] = ta.cci(df['high'], df['low'], df['close'], length)
    return df.loc[:,['timestamp', 'cci']].to_json()

@eel.expose
def get_bb(timestamp, close, length):
    print(f'get_bb: length={length}')
    df = pd.DataFrame()
    df['timestamp'] = pd.DataFrame.from_dict(timestamp, orient='index')
    df['close'] = pd.DataFrame.from_dict(close, orient='index')

    df_bbands = ta.bbands(df['close'], length)
    df_bbands['timestamp'] = df['timestamp']
    df = df.merge(df_bbands, on='timestamp')

    return df.loc[:,['timestamp', f'BBL_{length}_2.0', f'BBM_{length}_2.0', f'BBU_{length}_2.0']].to_json()

@eel.expose
def run_backtest(ohlcv, module_name: str, method_name: str, size: Decimal):
    print(f'run_backtest: module_name={module_name}, method_name={method_name}, size={size}')

    # 実行フォルダをインポートパスに追加
    print(os.getcwd())
    sys.path.append(os.getcwd())

    df = pd.DataFrame(ohlcv)
    print(df)

    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        print('Not Module: ' + str(e))
        return

    try:
        method = getattr(module, method_name)
    except Exception as e:
        print('Not Method: ' + str(e))
        return
    
    try:

        backtest_data = []
        for idx in range(len(df)):
            ohlcv = df[0:idx+1]

            # バックテスト
            ret: Dict = method(ohlcv)

            if ret is not None:
                order_datetime = utility.timestampToDatetime(str(ret['timestamp']))
                ret['datetime'] = utility.str_format_datetime(order_datetime)
                ret['drawdown'] = ret['price']
                ret['position'] = False
                ret['position_datetime'] = None
                ret['execution'] = False
                ret['execution_price'] = 0
                ret['execution_datetime'] = None
                ret['profit'] = 0

                backtest_data.append(ret)
                pass

            for idx in range(len(backtest_data)):
                if backtest_data[idx]['position'] == False:
                    # 注文 → ポジション
                    if ohlcv['low'].iloc[-1] <= backtest_data[idx]['price'] <= ohlcv['high'].iloc[-1]:
                        backtest_data[idx]['position'] = True
                        position_datetime = utility.timestampToDatetime(str(ohlcv['timestamp'].iloc[-1]))
                        backtest_data[idx]['position_datetime'] = utility.str_format_datetime(position_datetime)
                        pass
                    pass
                elif backtest_data[idx]['execution'] == False:
                    # ドローダウン
                    if backtest_data[idx]['type'] == 0:
                        # Sell marker
                        if backtest_data[idx]['drawdown'] < ohlcv['high'].iloc[-1]:
                            backtest_data[idx]['drawdown'] = ohlcv['high'].iloc[-1]
                        pass
                    else:
                        # Buy marker
                        if ohlcv['low'].iloc[-1] < backtest_data[idx]['drawdown']:
                            backtest_data[idx]['drawdown'] = ohlcv['low'].iloc[-1]
                        pass
                    pass
                    # ポジション → 約定
                    if backtest_data[idx]['type'] != backtest_data[len(backtest_data)-1]['type']:
                        backtest_data[idx]['execution'] = True
                        backtest_data[idx]['execution_price'] = backtest_data[len(backtest_data)-1]['price']
                        position_datetime = utility.timestampToDatetime(str(ohlcv['timestamp'].iloc[-1]))
                        backtest_data[idx]['execution_datetime'] = utility.str_format_datetime(position_datetime)
                        if backtest_data[idx]['type'] == 0:
                            # Sell marker
                            backtest_data[idx]['profit'] = (backtest_data[idx]['price'] - backtest_data[idx]['execution_price']) * size
                            pass
                        else:
                            # Buy marker
                            backtest_data[idx]['profit'] = (backtest_data[idx]['execution_price'] - backtest_data[idx]['price']) * size
                            pass
                        pass
                    pass
                pass

        result_df = pd.DataFrame(backtest_data)
        print(result_df)
        return result_df.to_json()

    except Exception as e: 
        print(e)
        return



if __name__ == '__main__':
    try:
        # run_backtest('strategy1', 'bb_strategy_directed')
        asyncio.run(main())
    except Exception as e:
        print(e)
        pass
