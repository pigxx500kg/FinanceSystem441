import hashlib
import re
import time
from datetime import datetime
import requests
import json
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import pymysql

# 初始化 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/finance_news'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 配置 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 定义 User 模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))

# 创建一个应用上下文并创建所有的数据库表
with app.app_context():
    db.create_all()

# 定义登陆表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    login = SubmitField('登录')
    register = SubmitField('注册')


# 定义用户加载函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 定义登陆视图
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if form.login.data:
            # 登陆操作
            if user is None or user.password != form.password.data:
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        elif form.register.data:
            # 注册操作
            if user is not None:
                flash('Username already exists')
                return redirect(url_for('login'))
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

from urllib import request as urequest
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

find = {
    1: re.compile(r'">(.*?)</a></td>'),
    2: re.compile(r'//.*?">(.*?)</a></td>'),
    6: re.compile(r'">(.*?)</td>'),
    7: re.compile(r'">(.*?)</td>'),
    8: re.compile(r'">(.*?)</td>')
}
global fundSharesList
fundSharesList = []




def handle(a):

    flag = False
    for i in range(0, len(fundSharesList)):
        if a[0] == fundSharesList[i][0]:
            fundSharesList[i][2] = round(float(fundSharesList[i][2]) + float(a[4]), 2)
            flag = True
            break
    if not flag:
        new = [a[0], a[1], a[2]]
        fundSharesList.append(new)



# engine = create_engine("mysql+pymysql://root:123456@localhost/finance_news?charset=utf8mb4")

def scrape_fund_shares():
    db = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        db='finance_news',
        charset='utf8mb4'
    )
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    global fundSharesList
    # ...爬虫代码...

    funds = []
    fundNum = 0
    errorNum = 0
    send = urequest.Request("http://fund.eastmoney.com/js/fundcode_search.js", headers=head)
    response = urequest.urlopen(send)
    js = response.read().decode('utf-8')
    js = js[11:len(js) - 3].split("],[")
    for i in range(0, len(js)):
        fund = str(js[i]).replace('"', '')
        fund = fund.split(",")
        funds.append(fund)

    while fundNum < 20:
        fund_id = funds[fundNum][0]

        try:
            url = "http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=" + str(
                fund_id) + "&topline=10&year=2020&month=&rt=0.21822537857648627"
            send = urequest.Request(url, headers=head)
            response = urequest.urlopen(send, timeout=10)
            html = response.read().decode('utf-8')
            bs = BeautifulSoup(html, "html.parser")

            find_list = bs.find_all("tbody")
            tr = find_list[0].find_all("tr")

            for i in tr:
                td = i.find_all("td")
                fundShares = []
                for j in range(0, len(td)):
                    if j in [1, 2, 6, 7, 8]:
                        a = re.findall(find[j], str(td[j]))[0]
                        if j == 6:
                            a = str(a).replace(",", "")
                            if (len(a) > 8):
                                time.sleep(6)
                        fundShares.append(a)
                handle(fundShares)

            errorNum = 0

        except Exception as e:
            if str(e) == "timed out" and errorNum <= 3:
                errorNum = errorNum + 1
                fundNum = fundNum - 1

        fundNum = fundNum + 1
        # if fundNum == 1000:
        #     break

    # 使用 cursor() 方法创建一个游标对象 cursor
    drop_table_query = "DROP TABLE IF EXISTS fundshares"
    cursor = db.cursor()
    cursor.execute(drop_table_query)
    db.commit()
    create_table_query = '''CREATE TABLE `fundshares`  (
                    `fundSharesId` VARCHAR(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '股票代码',
                    `fundSharesName` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '股票名称',
                    `fundSharesMoney` DOUBLE(255, 2) NULL DEFAULT NULL COMMENT '金额（万元）',
                    UNIQUE INDEX `unique`(`fundSharesId`) USING BTREE
                    ) ENGINE = INNODB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = DYNAMIC'''
    cursor.execute(create_table_query)
    db.commit()
    try:
        for insert in fundSharesList:
            sql = "INSERT INTO fundShares VALUES ('" + str(insert[0]) + "', '" + str(insert[1]) + "', " + str(
                insert[2]) + ");"
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
    except Exception as e:
        # 回滚
        db.rollback()
        raise Exception("插入数据库错误！", e)

    # try:

    df = pd.DataFrame(fundSharesList, columns=['id', 'name', 'amount'])
    #     df.to_sql('fund_shares', con=engine, if_exists='replace', index=False)
    # except Exception as e:
    # # 回滚
    #     db.rollback()
    #     raise Exception("插入数据库错误！", e)

    # 关闭数据库连接
    db.close()


    fundSharesList = []
    return df

@app.route('/scrape_fund_shares', methods=['POST'])
def scrape_fund_shares_route():
    df = scrape_fund_shares()
    data = df.to_dict('records')
    return render_template('fund_shares.html', data=data)

#
# @app.route('/fund_shares')
# def fund_shares():
#     df = pd.read_sql_query("SELECT * FROM fund_shares", con=engine)
#
#     data = df.to_dict('records')
#     return render_template('fund_shares.html', data=data)




def east_fin_news(keyword):
    """
    东方财富-个股新闻
    keyword:关键词
    """
    url = "https://search-api-web.eastmoney.com/search/jsonp"
    params = {
        "cb": "jQuery3510875346244069884_1668256937995",
        "param": '{"uid":"",'
                 + f'"keyword":"{keyword}"'
                 + ',"type":["cmsArticleWebOld"],"client":"web","clientType":"web","clientVersion":"curr","param":{"cmsArticleWebOld":{"searchScope":"default","sort":"default","pageIndex":1,"pageSize":100,"preTag":"<em>","postTag":"</em>"}}}',
        "_": "1668256937996",
    }
    res = requests.get(url, params=params)
    data_text = res.text
    data_json = json.loads(
        data_text.strip("jQuery3510875346244069884_1668256937995(")[:-1]
    )
    df = pd.DataFrame(data_json["result"]["cmsArticleWebOld"])
    df['title'] = df['title'].apply(lambda s: re.sub('[\(<em></em>\<em></em>]', '', s))
    df['content'] = df['content'].apply(lambda s: re.sub('[\(<em></em>\<em></em>]', '', s))
    df['keyword'] = keyword
    df = df[['date', 'keyword', 'title', 'content', 'url']]
    df = df.reindex(columns=['date', 'title', 'url'])
    # 返回的df 包含 date, title, url
    old_columns = df.columns.tolist()
    new_columns = ['发布时间', '标题', 'url']
    # 使用字典构建列名映射关系
    columns_mapping = dict(zip(old_columns, new_columns))
    # 使用rename()方法重命名列
    df = df.rename(columns=columns_mapping)
    df = df.sort_values('发布时间', ascending=False)
    return df

@login_required
def cls_news():
    """
    财联社-电报
    :return: 财联社-电报
    :rtype: pandas.DataFrame
    """
    current_time = int(time.time())
    url = "https://www.cls.cn/nodeapi/telegraphList"
    params = {
        "app": "CailianpressWeb",
        "category": "",
        "lastTime": current_time,
        "last_time": current_time,
        "os": "web",
        "refresh_type": "1",
        "rn": "2000",
        "sv": "7.7.5",
    }
    text = requests.get(url, params=params).url.split("?")[1]
    if not isinstance(text, bytes):
        text = bytes(text, "utf-8")
    sha1 = hashlib.sha1(text).hexdigest()
    keyword = hashlib.md5(sha1.encode()).hexdigest()

    params = {
        "app": "CailianpressWeb",
        "category": "",
        "lastTime": current_time,
        "last_time": current_time,
        "os": "web",
        "refresh_type": "1",
        "rn": "2000",
        "sv": "7.7.5",
        "sign": keyword,
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Host": "www.cls.cn",
        "Pragma": "no-cache",
        "Referer": "https://www.cls.cn/telegraph",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }
    data = requests.get(url, headers=headers, params=params).json()
    df = pd.DataFrame(data["data"]["roll_data"])
    df = df[["title", "content", "ctime"]]
    df["ctime"] = pd.to_datetime(
        df["ctime"], unit="s", utc=True
    ).dt.tz_convert("Asia/Shanghai")
    df.columns = ["标题", "内容", "发布时间"]
    df.sort_values(["发布时间"], inplace=True, ascending= False)
    df.reset_index(inplace=True, drop=True)
    df['发布时间'] = df['发布时间'].astype(str).str[:-6]
    df = df.reindex(columns=['发布时间', '内容'])
    return df





def save_to_mysql(keyword, df):
    # 连接到数据库
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='finance_news',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # 替换已存在的表
    table_name = f'east_fin_{keyword}'
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

    # 创建新表
    with connection.cursor() as cursor:
        create_table_query = f"""CREATE TABLE `{table_name}` (
                                `发布时间` datetime,
                                `标题` varchar(255),
                                `链接` varchar(255)
                                )"""
        cursor.execute(create_table_query)

    # 插入数据
    with connection.cursor() as cursor:
        for _, row in df.iterrows():
            insert_query = f"""INSERT INTO `{table_name}` (`发布时间`, `标题`, `链接`)
                               VALUES ('{row['发布时间']}', '{row['标题']}', '{row['url']}')"""
            cursor.execute(insert_query)

    # 提交更改并关闭连接
    connection.commit()
    connection.close()


def save_cls_to_mysql(keyword, df):
    # 连接到数据库
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='finance_news',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # 创建新表
    table_name = f'cls_news_{datetime.now().strftime("%Y%m%d%M%S")}'
    with connection.cursor() as cursor:
        create_table_query = f"""CREATE TABLE `{table_name}` (
                                `发布时间` datetime,
                                `内容` varchar(1024)
                                )"""
        cursor.execute(create_table_query)

    # 插入数据
    with connection.cursor() as cursor:
        for _, row in df.iterrows():
            insert_query = f"""INSERT INTO `{table_name}` (`发布时间`, `内容`)
                               VALUES ('{row['发布时间']}', '{row['内容']}')"""
            cursor.execute(insert_query)

    # 提交更改并关闭连接
    connection.commit()
    connection.close()



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

