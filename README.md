### 1.安装

  #### 1.1 安装pywin32库
  解析xlsx文件需要安装pywin32，注意文件比较大，采用国内镜像可以大大加快速度，在cmd如下输入：  
  pip intall -i https://pypi.tuna.tsinghua.edu.cn/simple pywin32

  若要一劳永逸，详情参见：  
  https://blog.csdn.net/fatfatmomo/article/details/81184119
  
  
  #### 1.2 防止导入win32模块时报错
  把..\AppData\Local\Programs\Python\Python37\lib\site-packages\win32  
  这个路径加到系统变量
  虽然我在这个项目中加入了一段代码可以避开这个报错，但是最好从源头解决这个问题
  详情：  
  https://blog.csdn.net/Andy_221313/article/details/105701918

  #### 1.3 下载Jmeter并加入到系统变量
  如果不需要需要在本地运行jmeter，可以跳过此步骤
  
  * 下载  
  jmeter官方下载速度太慢，这里有一个百度盘分享(apache-jmeter-5.2.1):  
  https://pan.baidu.com/s/1vM2UpUqjGcjpeJsStCNJoQ  
  密码:x0l2  
  
  * 系统变量设置  
  参见：https://www.cnblogs.com/become/p/11646707.html  
  最后需要在系统环境变量加入%JMETER_HOME%\bin;  
   
  
  #### 1.4 selenium库的使用
  该项目中爬取showdoc和禅道中的网页信息需要用到selenium
  
  * 安装库  
  在cmd中输入:  
  pip intall -i https://pypi.tuna.tsinghua.edu.cn/simple selenium  
  如果已经参考：  
  https://blog.csdn.net/fatfatmomo/article/details/81184119  
  配置好了pip的下载终端，则只需要输入:  
  pip intall selenium  
  
  * 安装chrome  
  下载地址：  
  https://www.google.cn/chrome/  
  
  * 下载chrome驱动器  
  先查看chrome的版本，查看方式参见：  
  https://jingyan.baidu.com/article/4853e1e59271851909f726fd.html  
  
  * 下载地址:  
  http://chromedriver.storage.googleapis.com/index.html  
  
  选择样式为××.×.××××.××的文件进入，下载符合自己电脑设置的zip文件  
  
  驱动器的版本号要大于chrome浏览器的版本号  
  
  * 配置:  
  将下载好的驱动器解压后的整个文件，放到安全的路径  
  比如：   
  C:\Users\Administrator\AppData\Local\Programs\Python\Python37\Tools\chromedriver_win32\chromedriver.exe  
  然后将具体路径复制粘贴在app文件中的config.txt文件中的第二行，覆盖原来的内容
  
  在配置文件config.txt中
  谷歌的配置文件目录在安装的时候是不可选的
  脚本按照默认的config.txt第一行路径去确认
  一般只在在Administrator这个文件上会各有不同，修改完第一行后保存
  
  * 注意事项：  
  selenium启动的浏览器的配置参数和手动点开chrome的是一样的，所以selenium启动前需要关闭chrome浏览器  
  
#### 2.运行流程：
  ##### 2.1 批量生成jmx文件  
  * 复制api_test_temp.xlsx，按照这个模版文件的规范填写测试用例，可任意改名为test.xlsx  
  * 将app/run.py这个文件中的xlsx_path的值改为:  
  xlsx_path = r'../../test.xlsx'  
  一定要是绝对路径，并且前面加上'r'，否则报错  
  * 如果修改了表单名（原名“pc端”），也要将xlsx_path下的sheet变量改为相应值
  * jmx_path, report_path分别是生成的jmx文件存放目录，与压测报告存放目录，参见[注意事项](#3注意事项)  
  函数generate_jmx_and_report_repository(xlsx_path)会根据xlsx_path所在父目录生成jmx_path, report_path这两个目录  
  也可以自行设置
  * 设置完毕后可以运行run.py，然后可以在jmx_path对应的目录中看到生成的jmx文件
  
  ##### 2.2 本地运行jmx文件
  * 建立一个ModifyJmx()对象：  
   m = ModifyJmx()  
   m.run_jmx(jmx_path,report_dir)  

  report_dir可为空，不为空时，只能一个一个测试，详情参见[注意事项](#3注意事项)
  
  
  
  
#### 3.注意事项
  * 使用jmeter本地压测时  
  待生成报告的路径文件夹必须为空，否则报错  
  报告路径是指使用ModifyJmx().run_jmx(report_dir)中的report_dir这个参数  
  用来存放对单一用例(一个jmx文件)的压测结果的分析文件，是一个html文件
  如果run_jmx(report_dir)中report_dir参数为空（不设置默认为空），则不生成报告，测试结果会记录在app目录下的log.jtl中  
  log.jtl可以直接改后缀名为.csv，即可得到货真价实的csv文件
  
  * jmx文件是要提交到阿里云进行压测的  
  如果有csv文件作为参数文件，路径只需要将模版表格中的Params设置为test.csv的相对路径形式  
  在上传到阿里云时，一并上传对应的csv文件
  
 
  



