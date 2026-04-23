from infra.push import push
from engine import run
from core.safe import safe_run

def main(stock_list):

    leaders = safe_run(run, [], stock_list)

    msg = "🏦 V2.5 稳定系统\n\n"

    msg += "🏆 龙头：\n"

    for l in leaders:
        msg += f"{l['code']} {l['name']}\n"

    push(msg)

if __name__ == "__main__":
    try:
        main([])
    except Exception as e:
        print("[CRITICAL]", e)
