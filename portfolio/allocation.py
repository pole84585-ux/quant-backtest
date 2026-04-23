def allocate(leaders, laggers):

    portfolio = []

    # 龙头 60%
    if leaders:
        w = 0.6 / len(leaders)
        for l in leaders:
            portfolio.append({
                "code": l["code"],
                "weight": w
            })

    # 补涨 30%
    if laggers:
        w = 0.3 / len(laggers)
        for l in laggers:
            portfolio.append({
                "code": l["code"],
                "weight": w
            })

    # 现金 10%
    portfolio.append({
        "code": "CASH",
        "weight": 0.1
    })

    return portfolio
