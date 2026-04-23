from core.leader import is_leader, strength
from core.lagger import is_lagger
from portfolio.allocation import allocate
from data.fetch import get_data

def run(stock_list, sector):

    leaders = []
    laggers = []

    for s in stock_list:

        df = get_data(s["code"])

        if df is None or len(df) < 30:
            continue

        sector_flag = True  # 简化：默认同板块（可扩展）

        if is_leader(df):

            leaders.append({
                "code": s["code"],
                "name": s["name"],
                "strength": strength(df)
            })

        elif is_lagger(df, sector_flag):

            laggers.append({
                "code": s["code"],
                "name": s["name"]
            })

    leaders = sorted(leaders, key=lambda x: x["strength"], reverse=True)[:3]

    portfolio = allocate(leaders, laggers)

    return leaders, laggers, portfolio
