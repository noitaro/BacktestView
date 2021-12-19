import asyncio
import pandas_ta as ta # pip install -U git+https://github.com/twopirllc/pandas-ta

async def main():
    
    pass

def bb_strategy_directed(ohlcv_df):
    LENGTH = 20
    print(f"bb_strategy_directed {LENGTH}")
    
    # ボリンジャーバンド計算
    bbands_df = ta.bbands(ohlcv_df['close'], LENGTH)
    if bbands_df is None: return

    crossover_df = ta.cross(ohlcv_df['close'], bbands_df['BBL_20_2.0'], True)
    crossunder_df = ta.cross(ohlcv_df['close'], bbands_df['BBU_20_2.0'], False)

    if crossover_df.iloc[-2] == 1:
        timestamp = ohlcv_df['timestamp'].iloc[-1]
        type = 1 # Buy marker
        price = ohlcv_df['close'].iloc[-2]
        label = 'BBandLE'

        return {'timestamp': timestamp, 'type': type, 'price': price, 'label': label}

    if crossunder_df.iloc[-2] == 1:
        timestamp = ohlcv_df['timestamp'].iloc[-1]
        type = 0 # Sell marker
        price = ohlcv_df['close'].iloc[-2]
        label = 'BBandSE'

        return {'timestamp': timestamp, 'type': type, 'price': price, 'label': label}


    return





if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception:
        pass
