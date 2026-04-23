from data.universe import get_universe
from core.sector import get_sector
from engine import run
from push import push

def main():

    stock_list = get_universe()
    sector = get_sector()

    leaders, laggers, portfolio = run(stock_list, sector)

    msg = "🏦 机构级市场结构系统\n\n"

    msg += f"🔥 板块：{sector['leader_sector']} ({sector['leader_change']}%)\n\n"

    msg += "🏆 龙头：\n"
    for l in leaders:
        msg += f"{l['code']} {l['name']} 强度:{round(l['strength'],2)}\n"

    msg += "\n🚀 补涨：\n"
    for l in laggers:
        msg += f"{l['code']} {l['name']}\n"

    msg += "\n💼 仓位：\n"
    for p in portfolio:
        msg += f"{p['code']} : {p['weight']*100:.1f}%\n"

    push(msg)

if __name__ == "__main__":
    main()
