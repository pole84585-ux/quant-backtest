import akshare as ak


def get_stock_list():
    df = ak.stock_info_a_code_name()

    def is_main(code):
        return code.startswith(("600","601","603","605","000","001"))

    df = df[df["code"].apply(is_main)]
    df = df[~df["name"].str.contains("ST")]

    return df


def get_hist(code):
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        df.columns = [
            "date","open","close","high","low",
            "volume","amount","_","_","_","_"
        ]
        return df
    except:
        return None


# ===== 行业数据（板块共振）=====
def get_industry():
    try:
        df = ak.stock_board_industry_name_em()
        return df
    except:
        return None
