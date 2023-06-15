import efinance as ef
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf


# 股票代码

# stock_code = '600519'
# df = ef.stock.get_quote_history(stock_code)
stock_name = "不好当家"
df = ef.stock.get_quote_history(stock_name)
if(len(df)!=0):
    # 确保日期列是datetime类型
    df['日期'] = pd.to_datetime(df['日期'])

    # 找出后半年的日期范围，以便筛选数据
    end_date = df['日期'].max()
    start_date = end_date - pd.DateOffset(months=6)
    df_half_year = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)].copy()

    # 设置日期为索引
    df_half_year.set_index('日期', inplace=True)

    # 对列名进行重命名，以符合mplfinance的要求
    df_half_year.rename(columns={'开盘':'Open', '收盘':'Close', '最高':'High', '最低':'Low', '成交量':'Volume'}, inplace=True)

    # 创建K线图
    mc = mpf.make_marketcolors(up='r',down='g') # 红涨绿跌
    s  = mpf.make_mpf_style(marketcolors=mc)
    mpf.plot(df_half_year, type='candle', style=s, ylabel='Price', volume=True)
    # mpf.plot(df_half_year, type='candle', style=s, title='K线图', ylabel='价格', volume=True)

    plt.show()
