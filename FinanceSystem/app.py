from login_register import *
from east_fin_fund_shares import *
from east_fin_news import *
from cls_realtime_news import *
from east_fin_stock_kplot import *

"""
app 目前有5个功能：
1.login_register.py: 注册、登录 
2.east_fin_news.py: 从东方财富网使用关键词搜索财经新闻
3.cls_realtime_news.py: 从财联社获取实时新闻资讯
4.east_fin_fund_shares.py: 获东方财富网基金持仓金额的获取
5.east_fin_stock_kplot.py: k线图的制作
"""


@app.route('/')
@login_required
def index():
    return render_template('function_index.html')


@app.route('/scrape_fund_shares', methods=['POST'])
def scrape_fund_shares_route():
    df = scrape_fund_shares()
    data = df.to_dict('records')
    return render_template('east_fin_fund_shares_result.html', data=data)


@app.route('/search', methods=['POST'])
@login_required
def search():
    keyword = request.form['keyword']
    df = east_fin_news(keyword)
    return render_template('east_fin_news_result.html', keyword=keyword, data=df.to_dict('records'))


@app.route('/get-news', methods=['POST'])
@login_required
def get_news():
    df = cls_realtime_news()
    return render_template('cls_realtime_news_result.html', data=df.to_dict('records'))


@app.route('/refresh', methods=['POST'])
@login_required
def refresh():
    keyword = request.form['keyword']
    df = cls_realtime_news()
    return render_template('cls_realtime_news_result.html', keyword=keyword, data=df.to_dict('records'))


@app.route('/save', methods=['POST'])
@login_required
def save():
    keyword = request.form['keyword']
    df = east_fin_news(keyword)
    save_to_mysql(keyword, df)
    return "结果已保存至 MySQL 数据库。"


@app.route('/save-cls-to-mysql', methods=['POST'])
@login_required
def save_cls_news_to_mysql():
    keyword = request.form['keyword']
    df = cls_realtime_news()
    save_cls_to_mysql(keyword, df)
    return "结果已保存至 MySQL 数据库。"


@app.route('/generate_k_plot', methods=['POST'])
@login_required
def generate_k_plot():
    stock_info = request.form['stock_info']
    title, kline_table = generate_k_plott(stock_info)
    if kline_table is None:
        # 如果没有生成图片，那么重定向到首页并显示错误信息
        return render_template('function_index.html', error="生成K线图失败，请检查输入的股票代码或名称")
    # 否则，将标题和K线图的路径传递给kplot.html进行渲染
    return render_template('east_fin_kplot_result.html', title=title, kline_table=kline_table)


if __name__ == '__main__':
    app.run()

