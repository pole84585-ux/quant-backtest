import os
from universe import get_universe
from data import get_kline
from factors import add_indicators
from score import stock_score
from sentiment import sentiment_score
from push import push

def run():

    print("🚀 开始运行系统...")

    df_list = get_universe().head(200)  # 防止超时

    results = []

    for _, row in df_list.iterrows():
        code = row["code"]
        name = row["name"]

        try:
            df = get_kline(code)
            if df is None or len(df) < 60:
                continue

            df = add_indicators(df)

            score = stock_score(df, code)
            senti = sentiment_score(code)

            final = score * 0.7 + senti * 30

            results.append((code, name, final))

        except Exception as e:
            print(f"❌ {code} 出错:", e)
            continue

    results = sorted(results, key=lambda x: x[2], reverse=True)[:10]

    msg = "📊 A股Top10\n\n"

    for r in results:
        msg += f"{r[0]} {r[1]} ⭐{r[2]}\n"

    push(msg)


if __name__ == "__main__":
    run()
