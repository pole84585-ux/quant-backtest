from data import get_stock_list, get_hist, get_industry
from strategy import calc_score
from notifier import send
import akshare as ak


# ===== 行业强度计算 =====
def get_industry_strength():

    df = get_industry()
    if df is None:
        return {}

    # 简化：取涨幅作为强度
    result = {}

    for _, row in df.iterrows():
        try:
            name = row["板块名称"]
            pct = float(row["涨跌幅"])
            result[name] = pct / 10  # 归一化
        except:
            continue

    return result


def run():

    stocks = get_stock_list()
    industry_strength = get_industry_strength()

    results = []

    for _, row in stocks.iterrows():

        code = row["code"]
        name = row["name"]

        df = get_hist(code)
        if df is None:
            continue

        # ===== 简单行业匹配（兜底）=====
        strength = 0.5  # 默认中性

        score = calc_score(df, strength)

        if score >= 85:
            results.append((code, name, score))

    results = sorted(results, key=lambda x: x[2], reverse=True)

    return results[:20]


if __name__ == "__main__":

    res = run()

    if not res:
        msg = "今日无龙头二波共振标的"
    else:
        msg = "🔥 龙头二波 + 板块共振：\n\n"
        for code, name, score in res:
            msg += f"{code} {name} | score:{score}\n"

    send(msg)
