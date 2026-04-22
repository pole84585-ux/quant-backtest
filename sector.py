import akshare as ak

def get_sector_strength():
    df = ak.stock_sector_spot_em()

    df = df.sort_values("涨跌幅", ascending=False)

    top = df.head(5)["板块名称"].tolist()

    return top
