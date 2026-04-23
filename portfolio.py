def build(selected):

    n = len(selected)

    if n == 0:
        return []

    weight = min(0.8 / n, 0.3)

    return [
        {"code": s[0], "name": s[1], "weight": round(weight, 2)}
        for s in selected
    ]
