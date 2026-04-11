import pandas as pd

def calc_future_return(df, buy_index, days=3):
    try:
        buy_price = df.iloc[buy_index]["收盘"]
        sell_price = df.iloc[buy_index + days]["收盘"]
        return (sell_price - buy_price) / buy_price
    except:
        return None


def backtest_signals(df, signals):
    results = []

    for i in signals:
        r3 = calc_future_return(df, i, 3)
        r5 = calc_future_return(df, i, 5)

        results.append({
            "index": i,
            "return_3d": r3,
            "return_5d": r5
        })

    return pd.DataFrame(results)
