# 使用案例: 腾讯词向量搜索服务

## 腾讯词向量说明

腾讯AI Lab开源大规模高质量中文词向量数据，800万中文词
说明页面：https://ai.tencent.com/ailab/nlp/zh/embedding.html
下载地址 ：https://ai.tencent.com/ailab/nlp/zh/data/Tencent_AILab_ChineseEmbedding.tar.gz

这个数据集提供了880万左右的词向量，维度为200

文件下载后大小为6.31G , 解压缩后大小为： 15.5G

## 向量提取处理 

如果不想自己提取数据，可以直接下载1万条数据，进入第二步启动向量搜索服务

由于文件是文本格式，需要进行一下处理，把词和向量分别保存到数据文件和向量文件中，以便于向量搜索服务加载。、

这里提供了一个转换工具，可直接对数据进行提取，
把上面解压后的文本文件`Tencent_AILab_ChineseEmbedding.txt`放到dat目录下即可；

以下是使用说明：

```
11:55:48.15|F:>python dataprocess.py -h
usage: dataprocess.py [-h] -datfile DATFILE [-outpath OUTPATH]
                      [-dofilter DOFILTER] [-topn TOPN]

腾讯词向量提取工具

optional arguments:
  -h, --help          show this help message and exit
  -datfile DATFILE    数据文件名
  -outpath OUTPATH    输出目录
  -dofilter DOFILTER  是否过滤非中文，默认=0不过滤
  -topn TOPN          截取前N个向量,默认=0不截取
```

由于数据量很大，这里用下面的命令提取前1万条，作一个示例：

```
python dataprocess.py -outpath=./top1w -dofilter=1 -topn=10000
```

运行结果：
```
11:59:30.66|F:>python dataprocess.py -outpath=./top1w -dofilter=1 -topn=10000
运行参数: Namespace(datfile='./dat/Tencent_AILab_ChineseEmbedding.txt', dofilter=1, outpath='./top1w', topn=10000)
开始转换向量,请稍等...
总记录数:8824330
[进度: 0.11% 已过滤:  196] 第9999   行: 债务
正在保存字典文件...
正在保存向量文件...
转换完成, 处理10000行，过滤196行，输出9804行。
```

为了便于测试，这里把1万条数据打包上传了，文件名：top1w.zip


### 启动向量搜索服务


使用向量搜索服务进行加载,10万条数据 ：

```
cd /mnt/sda1/transdat/sentence-similarity/vector_server
python VecSearch_faiss_server.py -npy='../tx_vector/top10w/vector.npy' -datfile='../tx_vector/top10w/keywords.txt'
```

服务端运行结果：
```
[2020-09-16 10:21:30,711]INFO 正在加载数据文件...
[2020-09-16 10:21:30,719]INFO 加载数据文件完成: ../tx_vector/top10w/keywords.txt
[2020-09-16 10:21:30,719]INFO 正在加载向量并创建索引器...
[2020-09-16 10:21:30,754]INFO 向量文件:../tx_vector/top10w/vector.npy
[2020-09-16 10:21:30,754]INFO 数据量:97115, 向量维度:200
[2020-09-16 10:21:30,754]INFO 距离计算方法:INNER_PRODUCT
[2020-09-16 10:21:30,754]INFO 监听端口:7800
[2020-09-16 10:21:31,402]INFO 索引创建完成，用时:0.682604秒
[2020-09-16 10:21:31,403]INFO Used Memory: 410.160 MB
[2020-09-16 10:21:31,413]INFO Running under Linux...
[2020-09-16 10:21:32,889]INFO 查询用时:2.20 毫秒
192.168.40.11 - - [2020-09-16 10:21:32] "POST /api/v0.1/sim HTTP/1.1" 200 225 0.008786
[2020-09-16 10:21:51,705]INFO 查询用时:1.49 毫秒
192.168.40.11 - - [2020-09-16 10:21:51] "POST /api/v0.1/sim HTTP/1.1" 200 227 0.002830
[2020-09-16 10:24:08,024]INFO 查询用时:1.80 毫秒
192.168.40.11 - - [2020-09-16 10:24:08] "POST /api/v0.1/sim HTTP/1.1" 200 227 0.003219

```

加载后可以使用CURL命令或者浏览器插件 PostWoman进行调用

880万向量全部加载大约需要120秒，内存28G，请注意环境并耐心等待。


