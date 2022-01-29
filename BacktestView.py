from typing import Dict
import eel # pip install eel
import ccxt # pip install ccxt
import asyncio
import pandas as pd  # pip install pandas
import pandas_ta as ta  # pip install -U git+https://github.com/twopirllc/pandas-ta
import sub_script as utility
import importlib
from decimal import Decimal
import os
import sys

# pip install PyInstaller
# python -m eel BacktestView.py web --onefile --noconsole --icon=Icojam-Animals-01-horse.ico


async def main():
    print(__file__)

    eel.init('web')
    eel.start('index.html', port=0, size=(1200, 800))

    pass


@eel.expose
def get_ohlcv(from_date: str, to_date: str):
    if from_date is None or from_date == '' or \
        to_date is None or to_date == '':
        return None

    print(f'get_ohlcv: FROM={from_date}, TO={to_date}')

    # 1609459200000 <- '2021-01-01'
    from_timestamp = utility.dateToTimestamp(from_date)
    to_timestamp = utility.dateToTimestamp(to_date)
    if from_timestamp >= to_timestamp:
        return None

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

    # timestamp -> datetime
    f_to_datetime = lambda x: utility.str_format_datetime(utility.timestampToDatetime(str(x)))
    ohlcv_df['datetime'] = ohlcv_df['timestamp'].map(f_to_datetime)

    return ohlcv_df.to_json()


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
