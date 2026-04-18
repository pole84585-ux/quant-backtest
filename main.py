from data import get_stock_list, get_hist
from strategy import calc_score
from notifier import safe_send


def run():

    results = []

    try:
        stocks = get_stock_list()
    except Exception as e:
        safe_send(f"❌ 获取股票列表失败: {e}")
        return results

    for _, row in stocks.iterrows():

        try:
            code = row.get("code")
            name = row.get("name")

            if not code:
                continue

            try:
                df = get_hist(code)
            except Exception as e:
                print(f"获取K线失败 {code}: {e}")
                continue

            if df is None or df.empty:
                continue

            try:
                score = calc_score(df)
            except Exception as e:
                print(f"计算失败 {code}: {e}")
                continue

            if score >= 85:
                results.append((code, name, score))

        except Exception as e:
            print(f"单股异常跳过: {e}")
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
        print("🔥 顶层异常已捕获:", repr(e))
        safe_send(f"系统异常: {e}")
