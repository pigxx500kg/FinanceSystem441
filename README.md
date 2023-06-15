# FinanceSystem441 - an excellent finance system
前置准备：  
  &emsp;&emsp;数据库准备： MySQL5.7.19   &emsp;MySQL8.0会报错  
      &emsp;&emsp;&emsp;&emsp;username: root  
      &emsp;&emsp;&emsp;&emsp;password: 123456  
      &emsp;&emsp;&emsp;&emsp;需要执行：create database finance_news  
  &emsp;&emsp;文件目录：  
      &emsp;&emsp;root:[FinanceSystem]  
      &emsp;&emsp;+--app.py  
      &emsp;&emsp;+--clsnews.py  
      &emsp;&emsp;+--finnews.py  
      &emsp;&emsp;+--fundshares.py  
      &emsp;&emsp;+--kplot.py  
      &emsp;&emsp;+--login.py  
      &emsp;&emsp;+--static  
      &emsp;&emsp; |  +--images  \[需要新建二级目录 root\static\images用于存放k线图]  
      &emsp;&emsp;+--templates  
      &emsp;&emsp; |  +--cls_result.html  
      &emsp;&emsp; |  +--fund_shares.html  
      &emsp;&emsp; |  +--index.html  
      &emsp;&emsp; |  +--kplot.html  
      &emsp;&emsp; |  +--login.html  
      &emsp;&emsp; |  +--result.html  
  
         
Finance System主要提供了4个功能  
      &emsp;&emsp;0.用户注册 / 用户登录  
      &emsp;&emsp;1.东方财经-关键词财经新闻查询  
      &emsp;&emsp;2.财联社电报-实时新闻资讯  
      &emsp;&emsp;3.东方财富-基金持仓信息获取  
      &emsp;&emsp;4.efinance-k线图\[支持股票代码查询与股票名称查询]  
