# TransmitSearchingTool

通过`selenuium`来对12306网页进行模拟访问，查询车次余票情况。

**特点：**

- 支持任意数量的中转换乘站点数。而12306官网只支持最多1次中转换乘站点的查询。
- 支持自定义中转换乘前后车次的间隔时间，限定最大值和最小值。

## 运行环境

1. selenium==3.141.0
2. tqdm==4.59.0
3. chrome浏览器
4. chrome浏览器对应版本的webdriver

## 运行

运行程序前，请先下载对应自己浏览器版本的[webdriver(chromedriver)](http://npm.taobao.org/mirrors/chromedriver/)，将下载文件解压得到的`chromedriver.exe`文件放到chrome浏览器主程序`chrome.exe`的同一文件夹下。

打开命令行，运行`12306.py`

```
python 12306.py --stations 深圳北 广州南 长沙南 武汉 郑州东 石家庄 北京西
```

参数说明：

- `--min-transmit-period`：最小中转间隔时间（单位：分钟，默认：20）
- `--max-transmit-period`：最大中转间隔时间（单位：分钟，默认：60）
- `--stations`：中转换乘站点。可以输入多个站点名，但必须是真实存在的站点名而不是所在城市。查询车票时会精确匹配站点名。
- `--time`：乘车日期（格式：YYYY-MM-DD，如：2022-01-22，默认：系统时间当天）
- `--port`：浏览器远程控制端口（默认：9221）

**注意1：**虽然程序理论上支持任意多个换乘站点，但是由于车次排列组合的关系，多个换乘站点可能会导致程序的输出特别多，有可能超出命令行窗口的最大限制行数，从而导致信息丢失。上面例子中7个站点的中转换乘方案就远远超出了命令行窗口的最大行数。

**注意2：**由于车次信息的打印需要一定的空间，所以请尽可能增大命令行窗口的宽度，使之能在一行内打印一趟车次信息。

## 结果

换乘区间的可购车票会全部列出，在输出最后会给出换乘方案，格式为：

```
换乘方案 A -> B -> C -> D :

车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
  车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
    车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
    车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
  车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
    车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...

车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
  车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
    车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
  车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
    车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
    车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
    车次: XXXXX, 时间: XX:XX-XX:XX, 历时: XX:XX, 商务座: XX, 一等座: ...
```

换乘方案将会以全展开目录的形式给出，不缩进的行为起始车次，每缩进一次代表与上方车次衔接的下级车次。

比如上面的例子中，第3,4,5行可以组成一个换乘方案；第3,4,6行、第3,7,8行、第10,13,15行等都可以各自组成一个换乘方案。

使用者可以根据自身出行的时间要求和座位档次要求对照方案中的车次信息来做出决定。

## TODO

- 增加网络不稳定时的鲁棒性和错误处理
- 将selenium改写成requests，抛弃浏览器的渲染，加速信息获取，提高易用度