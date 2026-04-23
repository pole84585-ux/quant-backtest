from universe import get_universe
from data import get_kline
from factors import add_indicators
from strategies import trend, breakout, pullback
from evaluator import evaluate
from allocator import allocate
from selector import select
from portfolio import build
from memory import load, save
from risk import check_drawdown
from push import push
import config

def run():

    state = load()

    universe = get_universe().head(config.MAX_STOCKS)

    strategy_scores = []

    for name, func in {
        "trend": trend,
        "breakout": breakout,
        "pullback": pullback
    }.items():

        total_score = 0

        for _, row in universe.iterrows():

            df = get_kline(row["code"])
            if df is None or len(df) < config.LOOKBACK:
                continue

            df = add_indicators(df)

            signal = func(df)

            score, _, _, _ = evaluate(df.tail(config.LOOKBACK), signal)

            total_score += score

        strategy_scores.append({"name": name, "score": total_score})

    weights = allocate(strategy_scores)

    stocks = []

    for _, row in universe.iterrows():

        df = get_kline(row["code"])
        if df is None:
            continue

        df = add_indicators(df)

        stocks.append({
            "code": row["code"],
            "name": row["name"],
            "trend": trend(df),
            "breakout": breakout(df),
            "pullback": pullback(df)
        })

    selected = select(stocks, weights)

    portfolio = build(selected)

    # 风控
    if check_drawdown(state["history"]):
        portfolio = []  # 清仓

    state["history"].append(len(portfolio))
    save(state)

    msg = "🤖 AI量化基金系统\n\n"

    for p in portfolio:
        msg += f"{p['code']} {p['name']} 仓位:{p['weight']}\n"

    push(msg)


if __name__ == "__main__":
    run()
