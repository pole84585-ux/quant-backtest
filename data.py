import akshare as ak
import pandas as pd
import os


CACHE_FILE = "stock_cache.csv"


# ========================
# 获取股票列表（稳定版）
# ========================
def get_stock_list():

    # ===== ① 主接口 =====
    try:
        print("尝试主接口...")
        df = ak.stock_info_a_code_name()

        if df is not None and not df.empty:
            df.columns = ["code", "name"]
            print(f"主接口成功: {len(df)}")

            save_cache(df)
            return df

    except Exception as e:
        print("主接口失败:", repr(e))


    # ===== ② 备用接口 =====
    try:
        print("尝试备用接口...")
        df = ak.stock_zh_a_spot()

        if df is not None and not df.empty:
            df = df[["代码", "名称"]]
            df.columns = ["code", "name"]

            print(f"备用接口成功: {len(df)}")

            save_cache(df)
            return df

    except Exception as e:
        print("备用接口失败:", repr(e))


    # ===== ③ 本地缓存兜底 =====
    if os.path.exists(CACHE_FILE):
        print("使用本地缓存...")
        df = pd.read_csv(CACHE_FILE)

        if not df.empty:
            print(f"缓存加载成功: {len(df)}")
            return df

    # ===== 最终失败 =====
    print("❌ 所有数据源失败")
    return pd.DataFrame(columns=["code", "name"])


# ========================
# 获取K线（带容错）
# ========================
def get_hist(code):

    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily")

        if df is None or df.empty:
            return None

        return df

    except Exception as e:
        print(f"K线失败 {code}:", e)
        return None


# ========================
# 缓存保存
# ========================
def save_cache(df):

    try:
        df.to_csv(CACHE_FILE, index=False)
        print("缓存已更新")
    except Exception as e:
        print("缓存保存失败:", e)
