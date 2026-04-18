import pandas as pd


# =========================
# 主评分函数（Pro版）
# =========================
def calc_score(df):

    if df is None or df.empty:
        return 0

    score = 0

    try:
        close = df["收盘"]

        # =========================
        # ① 趋势强度（30分）
        # =========================
        if close.iloc[-1] > close.iloc[-5] > close.iloc[-10]:
            score += 30

        # 均线多头（简化版）
        ma5 = close.rolling(5).mean()
        ma10 = close.rolling(10).mean()

        if ma5.iloc[-1] > ma10.iloc[-1]:
            score += 10


        # =========================
        # ② 龙头二波结构（25分）
        # =========================
        high_20 = close.max()
        pullback = close.iloc[-10:].min()

        # 回踩不破前高80%
        if pullback > high_20 * 0.75:
            score += 15

        # 近期重新走强
        if close.iloc[-1] > close.iloc[-3]:
            score += 10


        # =========================
        # ③ 量能（20分）
        # =========================
        vol = df["成交量"]

        if vol.iloc[-1] > vol.rolling(5).mean().iloc[-1]:
            score += 10

        if vol.iloc[-1] > vol.iloc[-2]:
            score += 10


        # =========================
        # ④ 波动健康度（10分）
        # =========================
        if close.std() / close.mean() < 0.15:
            score += 10


        # =========================
        # ⑤ 防垃圾股（减分）
        # =========================
        if close.iloc[-1] < 5:
            score -= 10

        if close.pct_change().std() > 0.08:
            score -= 10


    except Exception as e:
        print("评分异常:", e)
        return 0

    return max(score, 0)


# =========================
# 排序筛选
# =========================
def select_top(stock_data):

    results = []

    for code, name, df in stock_data:

        try:
            score = calc_score(df)

            if score >= 70:   # 🔥入选阈值
                results.append((code, name, score))

        except:
            continue

    return sorted(results, key=lambda x: x[2], reverse=True)[:20]
