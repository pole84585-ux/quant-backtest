from core.safe import safe_run
from core.leader import is_leader

def run(stock_list):

    leaders = []

    for s in stock_list:

        def process():
            df = s["df"]

            if is_leader(df):
                return {
                    "code": s["code"],
                    "name": s["name"]
                }

        res = safe_run(process)

        if res:
            leaders.append(res)

    return leaders
