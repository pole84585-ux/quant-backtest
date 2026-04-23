def select(stocks, weights):

    selected = []

    for s in stocks:

        score = 0

        if s["trend"]:
            score += weights.get("trend", 0)

        if s["breakout"]:
            score += weights.get("breakout", 0)

        if s["pullback"]:
            score += weights.get("pullback", 0)

        selected.append((s["code"], s["name"], score))

    selected = sorted(selected, key=lambda x: x[2], reverse=True)

    return selected[:5]
