import akshare as ak
import pandas as pd

def get_data(code):

    df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

    df = df.rename(columns={
        "收盘": "close",
        "成交量": "volume"
    })

    return df
