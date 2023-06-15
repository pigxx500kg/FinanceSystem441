#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import time
import pandas as pd

import pymysql
from urllib import request as urequest
from bs4 import BeautifulSoup

global fundSharesList
fundSharesList = []

find = {
    1: re.compile(r'">(.*?)</a></td>'),
    2: re.compile(r'//.*?">(.*?)</a></td>'),
    6: re.compile(r'">(.*?)</td>'),
    7: re.compile(r'">(.*?)</td>'),
    8: re.compile(r'">(.*?)</td>')
}

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

