#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import time
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import pymysql
from urllib import request as urequest
from bs4 import BeautifulSoup

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

