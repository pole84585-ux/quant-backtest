def score(df):

    df = df.copy()
    df['score'] = 0

    # 涨幅强度
    df['score'] += df['涨跌幅'] * 3

    # 成交量
    df['score'] += (df['成交量'] / df['成交量'].mean()) * 20

    # 活跃度
    df['score'] += (df['换手率'] < 20) * 10

    # 强势加成
    df['score'] += (df['涨跌幅'] > 3) * 10

    return df.sort_values('score', ascending=False)
