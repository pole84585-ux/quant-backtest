def check_drawdown(history):

    if not history:
        return False

    peak = max(history)
    current = history[-1]

    dd = (peak - current) / peak

    return dd > 0.15
