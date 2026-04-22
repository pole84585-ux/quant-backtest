import akshare as ak

def get_kline(code):
    return ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")


def get_sector(code):
    return "科技"
