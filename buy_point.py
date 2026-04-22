def buy_point(stage):

    if stage == "PIT":
        return "🕳 低吸观察（黄金坑）"

    elif stage == "BREAKOUT":
        return "🚀 可试仓（起爆点）"

    elif stage == "TREND":
        return "📈 持有/加仓（主升浪）"

    elif stage == "LEADER":
        return "🔥 强趋势核心（龙头）"

    else:
        return "❌ 回避"
