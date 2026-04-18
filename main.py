from data import get_stock_list, get_hist
from strategy import calc_score
from notifier import send


def run():

    stocks = get_stock_list()
    results = []

    for _, row in stocks.iterrows():

        code = row["code"]
        name = row["name"]

        df = get_hist(code)

        score = calc_score(df)

        if score >= 85:
            results.append((code, name, score))

    results = sorted(results, key=lambda x: x[2], reverse=True)

    return results[:20]


if __name__ == "__main__":

    res = run()

    if not res:
        msg = "今日无龙头二波共振标的"
    else:
        msg = "🔥 龙头二波 + 板块共振：\n\n"
        for code, name, score in res:
            msg += f"{code} {name} | score:{score}\n"

    send(msg)
