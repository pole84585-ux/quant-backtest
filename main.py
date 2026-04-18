from data import get_stock_list, get_hist
from strategy import calc_score
from notifier import safe_send


def run():

    try:
        stocks = get_stock_list()
    except Exception as e:
        safe_send(f"数据获取失败: {e}")
        return []

    results = []

    for _, row in stocks.iterrows():

        try:
            code = row["code"]
            name = row["name"]

            df = get_hist(code)

            score = calc_score(df)

            if score >= 85:
                results.append((code, name, score))

        except Exception as e:
            # ⭐单股票失败不影响整体
            print(f"跳过异常股票: {e}")
            continue

    return sorted(results, key=lambda x: x[2], reverse=True)[:20]


if __name__ == "__main__":

    try:
        res = run()

        if not res:
            msg = "今日无龙头二波共振标的"
        else:
            msg = "🔥 龙头二波 + 板块共振：\n\n"
            for code, name, score in res:
                msg += f"{code} {name} | score:{score}\n"

        safe_send(msg)

    except Exception as e:
        # ⭐最顶层兜底（永不崩）
        print("系统异常但已捕获:", repr(e))
