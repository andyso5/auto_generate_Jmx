1.解析xlsx文件需要安装pywin32，注意文件比较大，采用国内镜像可以大大加快速度，如下输入：
pip intall -i https://pypi.tuna.tsinghua.edu.cn/simple pywin32

  详情参见：https://blog.csdn.net/fatfatmomo/article/details/81184119

2.把..\AppData\Local\Programs\Python\Python37\lib\site-packages\win32
  这个路径加到系统变量，详情：https://blog.csdn.net/Andy_221313/article/details/105701918

3.Jmeter需要加入到系统变量
  参见：https://www.cnblogs.com/become/p/11646707.html

  最后需要在系统环境变量加入%JMETER_HOME%\bin;

4.注意：
  待生成报告的路径文件夹必须为空,上一次生成的log.jtl也必须移走或删除

5.如果需要用到网页登陆：https://showdoc.dev.yitong.com 获取数据

  需要安装谷歌浏览器：https://www.google.cn/chrome/

  下载对应chrome版本驱动插件:http://chromedriver.storage.googleapis.com/index.html


  如何查看chrome版本:https://jingyan.baidu.com/article/4853e1e59271851909f726fd.html

  将下载好的插件解压，放到安全的地方，比如：C:\Users\Administrator\AppData\Local\Programs\Python\Python37\Tools

  然后将路径复制粘贴在app文件中的config.txt文件中的第二行，覆盖原来的内容

  谷歌的配置文件目录在安装的时候是不可选的，所以按照默认的config.txt第一行路径去确认，一般只在在Administrator这个文件上会各有不同，然后把路径覆盖第一行

  6.注意：
      由于这个配置是本地的，所以用selenium启动前需要关闭谷歌浏览器，不然会冲突报错

"# auto_generate_jmx" 
