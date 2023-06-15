import os
import efinance as ef
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib as mpl
import time
mpl.rc("font", family='Microsoft YaHei')
mpl.use("TkAgg")

def generate_k_plott(stock_info):
    df = ef.stock.get_quote_history(stock_info)
    if len(df) == 0:
        return None, None
    df['日期'] = pd.to_datetime(df['日期'])
    title = df.loc[0, '股票名称'] + "半年K线图"
    end_date = df['日期'].max()
    start_date = end_date - pd.DateOffset(months=6)
    df_half_year = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)].copy()
    df_half_year.set_index('日期', inplace=True)
    df_half_year.rename(columns={'开盘':'Open', '收盘':'Close', '最高':'High', '最低':'Low', '成交量':'Volume'}, inplace=True)
    mc = mpf.make_marketcolors(up='r', down='g')
    s  = mpf.make_mpf_style(marketcolors=mc, rc={'font.family': 'Microsoft Yahei'})
    img_name = "k_plot_" + str(time.time()) + ".png"
    img_path = os.path.join("static/images", img_name)
    mpf.plot(df_half_year, type='candle', style=s, title=title, ylabel='价格', volume=True, savefig=img_path)
    return title, img_path

