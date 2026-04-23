import akshare as ak

def get_sector():

    df = ak.stock_sector_spot_em()

    df = df.sort_values("涨跌幅", ascending=False)

    return {
        "leader_sector": df.iloc[0]["板块名称"],
        "leader_change": df.iloc[0]["涨跌幅"]
    }
