import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# ==============================
# 获取全部A股列表
# ==============================
def get_all_stocks():
    df = ak.stock_info_a_code_name()
    df.columns = ["code", "name"]
    return df


# ==============================
# 判断是否主板股票
# ==============================
def is_main_board(code):
    # 沪市主板：600 / 601 / 603 / 605
    if code.startswith(("600", "601", "603", "605")):
        return True

    # 深市主板：000 / 001 / 002
    if code.startswith(("000", "001", "002")):
        return True

    return False


# ==============================
# 判断是否ST
# ==============================
def is_st(name):
    return ("ST" in name) or ("*ST" in name)


# ==============================
# 判断是否次新股（上市<120天）
# ==============================
def is_new_stock(code):
    try:
        df = ak.stock_individual_info_em(symbol=code)

        # 有些返回不同字段名，做兼容
        for col in df.columns:
            if "上市时间" in col:
                list_date = str(df[col].values[0])
                break
        else:
            return False

        list_date = datetime.strptime(list_date, "%Y-%m-%d")
        if datetime.now() - list_date < timedelta(days=120):
            return True

    except:
        return False

    return False


# ==============================
# 最终股票池（核心函数）
# ==============================
def get_universe():

    df = get_all_stocks()

    result = []

    for _, row in df.iterrows():
        code = row["code"]
        name = row["name"]

        # 1. 主板
        if not is_main_board(code):
            continue

        # 2. 剔除ST
        if is_st(name):
            continue

        # 3. 剔除次新股
        if is_new_stock(code):
            continue

        result.append({
            "code": code,
            "name": name
        })

    return pd.DataFrame(result)


# ==============================
# 测试用
# ==============================
if __name__ == "__main__":
    u = get_universe()
    print("股票数量:", len(u))
    print(u.head())
