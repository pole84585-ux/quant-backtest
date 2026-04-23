def allocate(strategy_scores):

    total = sum([s["score"] for s in strategy_scores if s["score"] > 0])

    weights = {}

    for s in strategy_scores:
        if total == 0:
            weights[s["name"]] = 0
        else:
            weights[s["name"]] = round(s["score"] / total, 2)

    return weights
