import akshare as ak
import pandas as pd
import os
from datetime import datetime


CACHE_FILE = "stock_pool_cache.csv"


# =========================
# 主函数：股票池获取（Pro）
# =========================
def get_stock_list():

    df = None

    # ========= ① 主接口 =========
    try:
        print("🔄 主接口获取股票列表...")
        df = ak.stock_info_a_code_name()

        df.columns = ["code", "name"]

    except Exception as e:
        print("❌ 主接口失败:", repr(e))


    # ========= ② 备用接口 =========
    if df is None or df.empty:
        try:
            print("🔄 备用接口...")
            df = ak.stock_zh_a_spot()

            df = df[["代码", "名称"]]
            df.columns = ["code", "name"]

        except Exception as e:
            print("❌ 备用接口失败:", repr(e))


    # ========= ③ 缓存兜底 =========
    if df is None or df.empty:
        if os.path.exists(CACHE_FILE):
            print("🧠 使用本地缓存股票池")
            df = pd.read_csv(CACHE_FILE)


    # ========= ④ 过滤规则 =========
    if df is not None and not df.empty:
        df = clean_stock_pool(df)
        save_cache(df)
        print(f"✅ 股票池最终数量: {len(df)}")
        return df


    print("❌ 股票池完全失败")
    return pd.DataFrame(columns=["code", "name"])


# =========================
# 股票过滤（核心Pro逻辑）
# =========================
def clean_stock_pool(df):

    # 转字符串防止报错
    df["code"] = df["code"].astype(str)

    # ===== ① 剔除 ST =====
    df = df[~df["name"].str.contains("ST")]

    # ===== ② 只保留主板 =====
    df = df[
        df["code"].str.startswith("000") |
        df["code"].str.startswith("001") |
        df["code"].str.startswith("002") |
        df["code"].str.startswith("600") |
        df["code"].str.startswith("601") |
        df["code"].str.startswith("603") |
        df["code"].str.startswith("605")
    ]

    return df.reset_index(drop=True)


# =========================
# K线数据（稳定版）
# =========================
def get_hist(code):

    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily")

        if df is None or df.empty:
            return None

        return df

    except Exception as e:
        print(f"⚠️ K线失败 {code}:", repr(e))
        return None


# =========================
# 缓存写入
# =========================
def save_cache(df):

    try:
        df.to_csv(CACHE_FILE, index=False)
    except Exception as e:
        print("⚠️ 缓存写入失败:", repr(e))
