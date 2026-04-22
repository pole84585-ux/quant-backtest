def max_drawdown_control(nav_curve):
    peak = max(nav_curve)
    current = nav_curve[-1]

    dd = (peak - current) / peak

    if dd > 0.15:
        return "REDUCE_RISK"

    return "OK"
