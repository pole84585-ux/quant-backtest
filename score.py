def stock_score(df):
    last = df.iloc[-1]

    score = 0

    if last["MA5"] > last["MA10"]:
        score += 30
    if last["MA10"] > last["MA20"]:
        score += 30
    if last["收盘"] > last["MA20"]:
        score += 40

    return score
