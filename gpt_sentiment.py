import openai
import config
import akshare as ak

openai.api_key = config.OPENAI_API_KEY


def gpt_sentiment(title_list):
    text = "\n".join(title_list[:10])

    prompt = f"""
你是A股量化分析师，请判断以下新闻对股票是：
正面 / 中性 / 负面，并给出0~1分情绪分数。

新闻：
{text}

只输出数字（0~1）
"""

    try:
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return float(res["choices"][0]["message"]["content"])

    except:
        return 0.5


def get_news_sentiment(code):
    try:
        df = ak.stock_news_em(symbol=code)
        titles = df["新闻标题"].tolist()
        return gpt_sentiment(titles)
    except:
        return 0.5
