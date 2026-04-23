import akshare as ak

def get_universe():

    df = ak.stock_info_a_code_name()

    # 剔除ST
    df = df[~df["name"].str.contains("ST")]

    # 只要主板
    df = df[df["code"].str.startswith(("60", "00"))]

    return df.to_dict("records")
