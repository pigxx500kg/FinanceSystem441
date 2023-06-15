#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import pandas as pd
import requests
import json
import pymysql

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


