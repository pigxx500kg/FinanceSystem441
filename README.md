# FinanceSystem441 - an excellent finance system
前置准备：  
  &emsp;&emsp;数据库准备： MySQL5.7.19   &emsp;MySQL8.0会报错  
      &emsp;&emsp;&emsp;&emsp;username: root  
      &emsp;&emsp;&emsp;&emsp;password: 123456  
      &emsp;&emsp;&emsp;&emsp;需要执行：create database finance_news  
  &emsp;&emsp;文件目录：注意创建好./static/image文件夹
&emsp;&emsp;&emsp;&emsp;root:[FinanceSystem]  
&emsp;&emsp;&emsp;&emsp;+--app.py  
&emsp;&emsp;&emsp;&emsp;+--cls_realtime_news.py  
&emsp;&emsp;&emsp;&emsp;+--east_fin_fund_shares.py  
&emsp;&emsp;&emsp;&emsp;+--east_fin_news.py  
&emsp;&emsp;&emsp;&emsp;+--east_fin_stock_kplot.py  
&emsp;&emsp;&emsp;&emsp;+--login_register.py  
&emsp;&emsp;&emsp;&emsp;+--static  
&emsp;&emsp;&emsp;&emsp;| +--images  
&emsp;&emsp;&emsp;&emsp;+--templates  
&emsp;&emsp;&emsp;&emsp;| +--cls_realtime_news_result.html  
&emsp;&emsp;&emsp;&emsp;| +--east_fin_fund_shares_result.html  
&emsp;&emsp;&emsp;&emsp;| +--east_fin_kplot_result.html  
&emsp;&emsp;&emsp;&emsp;| +--east_fin_news_result.html  
&emsp;&emsp;&emsp;&emsp;| +--function_index.html  
&emsp;&emsp;&emsp;&emsp;| +--login_register.html  

  
         
Finance System主要提供了4个功能  
      &emsp;&emsp;0.用户注册 / 用户登录  
      &emsp;&emsp;1.东方财经-关键词财经新闻查询  
      &emsp;&emsp;2.财联社电报-实时新闻资讯  
      &emsp;&emsp;3.东方财富-基金持仓信息获取  
      &emsp;&emsp;4.efinance-k线图\[支持股票代码查询与股票名称查询]  
