# FinanceSystem441 - an excellent finance system
前置准备：
  数据库准备 MySQL5.7.19 
      localhost: username
      password: 123456
      需要执行：create database finance_news
  文件目录：
      root:[FinanceSystem]
      +--app.py
      +--clsnews.py
      +--finnews.py
      +--fundshares.py
      +--kplot.py
      +--login.py
      +--static
      | +--images  \[需要新建二级目录 root\static\images用于存放k线图]
      +--templates
      | +--cls_result.html
      | +--fund_shares.html
      | +--index.html
      | +--kplot.html
      | +--login.html
      | +--result.html
主要提供了4个功能
0.用户注册 / 用户登录
1.东方财经-关键词财经新闻查询
2.财联社电报-实时新闻资讯
3.东方财富-基金持仓信息获取
4.efinance-k线图\[支持股票代码查询与股票名称查询]
