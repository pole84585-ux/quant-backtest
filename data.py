import akshare as ak

def get_data():

    df = ak.stock_zh_a_spot_em()

    # 只保留沪深主板
    df = df[df['代码'].str.startswith(('60','00'))]

    return df
