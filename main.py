from data import get_stock_list, get_hist
from strategy import calc_score
from notifier import send

import akshare as ak


def get_money(code):
    try:
        return ak.stock_individual_fund_flow(stock=code)
    except:
        return None


def run():
    stocks = get_stock_list()
    results = []

    for _, row in stocks.iterrows():

        code = row["code"]
        name = row["name"]

        df = get_hist(code)
        if df is None:
            continue

        money = get_money(code)

        score = calc_score(df, money)

        if score >= 80:
            results.append((code, name, score))

    results = sorted(results, key=lambda x: x[2], reverse=True)

    return results[:20]


if __name__ == "__main__":

    res = run()

    if not res:
        msg = "今日无龙头二波标的"
    else:
        msg = "🔥 龙头二波候选：\n\n"
        for code, name, score in res:
            msg += f"{code} {name} | score:{score}\n"

    send(msg)
