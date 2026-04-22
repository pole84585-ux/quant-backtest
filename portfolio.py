def build_portfolio(stocks):
    total = sum([s["score"] for s in stocks])

    portfolio = []

    for s in stocks:
        weight = s["score"] / total
        portfolio.append({
            "code": s["code"],
            "weight": round(weight, 3)
        })

    return portfolio
