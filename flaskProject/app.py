import hashlib
import re
import time
from datetime import datetime
import requests
import json
import pandas as pd
import pymysql
from flask import Flask, render_template, request

app = Flask(__name__)


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




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    df = east_fin_news(keyword)
    return render_template('result.html', keyword=keyword, data=df.to_dict('records'))


@app.route('/get-news', methods=['POST'])
def get_news():
    df = cls_news()
    return render_template('cls_result.html', data=df.to_dict('records'))


@app.route('/refresh', methods=['POST'])
def refresh():
    keyword = request.form['keyword']
    df = cls_news()
    return render_template('cls_result.html', keyword=keyword, data=df.to_dict('records'))


@app.route('/save', methods=['POST'])
def save():
    keyword = request.form['keyword']
    df = east_fin_news(keyword)
    save_to_mysql(keyword, df)
    return "结果已保存至 MySQL 数据库。"


@app.route('/save-cls-to-mysql', methods=['POST'])
def save_cls_news_to_mysql():
    keyword = request.form['keyword']
    df = cls_news()
    save_cls_to_mysql(keyword, df)
    return "结果已保存至 MySQL 数据库。"


if __name__ == '__main__':
    app.run()
