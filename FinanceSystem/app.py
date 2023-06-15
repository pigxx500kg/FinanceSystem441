
from login import *
from fundshares import *
from finnews import *
from clsnews import *


@app.route('/scrape_fund_shares', methods=['POST'])
def scrape_fund_shares_route():
    df = scrape_fund_shares()
    data = df.to_dict('records')
    return render_template('fund_shares.html', data=data)

#
# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
@login_required
def search():
    keyword = request.form['keyword']
    df = east_fin_news(keyword)
    return render_template('result.html', keyword=keyword, data=df.to_dict('records'))


@app.route('/get-news', methods=['POST'])
@login_required
def get_news():
    df = cls_news()
    return render_template('cls_result.html', data=df.to_dict('records'))


@app.route('/refresh', methods=['POST'])
@login_required
def refresh():
    keyword = request.form['keyword']
    df = cls_news()
    return render_template('cls_result.html', keyword=keyword, data=df.to_dict('records'))


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
    df = cls_news()
    save_cls_to_mysql(keyword, df)
    return "结果已保存至 MySQL 数据库。"


if __name__ == '__main__':
    app.run()

