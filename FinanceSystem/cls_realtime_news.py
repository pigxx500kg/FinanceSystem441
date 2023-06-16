import hashlib
from datetime import datetime
import requests
import time
import pandas as pd
import pymysql


def cls_realtime_news():
    """
    财联社-电报
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
    df.sort_values(["发布时间"], inplace=True, ascending=False)
    df.reset_index(inplace=True, drop=True)
    df['发布时间'] = df['发布时间'].astype(str).str[:-6]
    df = df.reindex(columns=['发布时间', '内容'])
    return df


def save_cls_to_mysql(keyword, df):
    # 连接到数据库
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='123456',
                                 db='finance_news',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # 创建新表
    table_name = f'cls_realtime_news_{datetime.now().strftime("%Y%m%d%M%S")}'
    with connection.cursor() as cursor:
        create_table_query = f"""CREATE TABLE `{table_name}` (
                                `发布时间` datetime,
                                `内容` varchar(8096)
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
