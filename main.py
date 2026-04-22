from universe import get_universe
from data import get_kline
from factors import add_indicators
from score import stock_score
from gpt_sentiment import get_news_sentiment
from sector import get_sector_strength
from portfolio import build_portfolio
from push import push

def run():

    universe = get_universe()
    hot_sectors = get_sector_strength()

    results = []

    for _, row in universe.iterrows():
        code = row["code"]
        name = row["name"]

        df = get_kline(code)
        if df is None or len(df) < 60:
            continue

        df = add_indicators(df)

        try:
            base = stock_score(df)
            senti = get_news_sentiment(code)

            final = base * 0.7 + senti * 30

            results.append({
                "code": code,
                "name": name,
                "score": final
            })

        except:
            continue

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:10]

    portfolio = build_portfolio(results)

    msg = "📊 A股终极量化组合Top10\n\n"

    for r in results:
        msg += f"{r['code']} {r['name']} ⭐{r['score']}\n"

    msg += "\n📦 组合权重:\n"

    for p in portfolio:
        msg += f"{p['code']} 权重:{p['weight']}\n"

    push(msg)


if __name__ == "__main__":
    run()
