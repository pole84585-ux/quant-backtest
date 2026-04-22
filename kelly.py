def kelly(win_rate, avg_win, avg_loss):
    if avg_loss == 0:
        return 0

    k = win_rate - ((1 - win_rate) / (avg_win / abs(avg_loss)))

    return max(0, min(k, 1))
