import requests
from data import get_data
from cycle import detect_cycle
from score import score
from buy_point import buy_point
from config import PUSHDEER_KEY


def push(msg):

    url = "https://api2.pushdeer.com/message/push"

    requests.post(url, data={
        "pushkey": PUSHDEER_KEY,
        "text": msg
    })


def main():

    df = get_data()

    df = detect_cycle(df)
    df = score(df)

    top = df.head(5)

    msg = "🚀 沪深主板主升浪系统\n\n"

    for _, row in top.iterrows():

        signal = buy_point(row['stage'])

        msg += (
            f"{row['代码']} {row['名称']}\n"
            f"阶段：{row['stage']}\n"
            f"信号：{signal}\n"
            f"涨幅：{row['涨跌幅']}%\n\n"
        )

    push(msg)


if __name__ == "__main__":
    main()
