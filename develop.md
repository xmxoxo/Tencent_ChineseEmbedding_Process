#【腾讯词向量】腾讯中文预训练词向量

【腾讯词向量】腾讯中文预训练词向量 - Yanqiang - 博客园  https://www.cnblogs.com/yanqiang/p/13536619.html


## 腾讯词向量介绍
腾讯词向量主页：https://ai.tencent.com/ailab/nlp/zh/embedding.html
词向量下载地址：https://ai.tencent.com/ailab/nlp/zh/data/Tencent_AILab_ChineseEmbedding.tar.gz

腾讯词向量（Tencent AI Lab Embedding Corpus for Chinese Words and Phrases）提供了预训练好的800万中文词汇的word embedding（200维词向量），可以应用于很多NLP的下游任务。

数据来源：新闻、网页、小说。
词表构建：维基百科、百度百科，以及Corpus-based Semantic Class Mining: Distributional vs. Pattern-Based Approaches论文中的方法发现新词。
训练方法：Directional Skip-Gram: Explicitly Distinguishing Left and Right Context for Word Embeddings论文中有介绍。

关于分词：可以使用任何开源分词工具，可以同时考虑细粒度和粗粒度的分词方式。
关于停用词、数字、标点：为了满足一些场景的需求，腾讯词向量并没有去掉这些，使用的时候需要自己构建词表并忽略其他无关词汇。

Tencent_AILab_ChineseEmbedding.txt文件内容：
第一行是词向量总数（8824330），和词向量维度（200）。
从第二行开始，每行是中文词以及它的词向量表示，每一维用空格分隔。


## 腾讯词向量使用举例

以查找近义词为例，介绍腾讯词向量的使用方法。

首先需要将已有的包含词和词向量的txt文件读入（使用KeyedVectors）

keyedVectors
可以很方便地从训练好的词向量中读取词的向量表示，快速生成 {词：词向量}
其中binary=False，加载的是txt文件，binary=True，加载的是二进制文件

然后构建词汇和索引的映射表，并用json格式离线保存，方便以后直接加载annoy索引时使用

基于腾讯词向量构建Annoy索引，annoy作用是在高维空间求近似最近邻
方法：
1、高维空间随意选两个点，做一个聚类数为2的kmeans，产生两个类，
每类有中心点，这两个点为基准，找到垂直于二者连线的超平面，可以区分出两个集合
2、现在变成了两个集合，分别再进行第一步
3、设定一个k，最终每个类最多剩余k个点，停止
4、以上面区分两个集合的方法构建二叉树
5、如果查某个点的最近邻点，就在二叉树里搜索

AnnoyIndex(f, metric)
returns a new index that's read-write and stores vector of f dimensions. Metric can be "angular", "euclidean", "manhattan", "hamming", or "dot".
返回一个可以读写的index，并存储f维向量，度量可以是夹角、欧几里得距离、曼哈顿距离、汉明距离和点积。默认是夹角。

tc_index.build(10)
n_trees is provided during build time and affects the build time and the index size. A larger value will give more accurate results, but larger indexes.
n_trees影响构建时间和index大小，n_trees更大，则结果更精确，但是index也就更大，官方文档示例默认的是10

a.build(n_trees)
builds a forest of n_trees trees. More trees gives higher precision when querying.
After calling build, no more items can be added.
构建一个有n_trees颗树的森林，树越多越精确。build完，就不能再增加了


```
import json
from collections import OrderedDict
from gensim.models import KeyedVectors
from annoy import AnnoyIndex

tc_wv_model = KeyedVectors.load_word2vec_format('Tencent_AILab_ChineseEmbedding.txt', binary=False)

# 把txt文件里的词和对应的向量，放入有序字典
word_index = OrderedDict()
for counter, key in enumerate(tc_wv_model.vocab.keys()):
    word_index[key] = counter
    
# 本地保存
with open('tc_word_index.json', 'w') as fp:
    json.dump(word_index, fp)
    
# 腾讯词向量是两百维的
tc_index = AnnoyIndex(200)
i = 0
for key in tc_wv_model.vocab.keys():
    v = tc_wv_model[key]
    tc_index.add_item(i, v)
    i += 1

tc_index.build(10)

# 将这份index存到硬盘
tc_index.save('tc_index_build10.index')

# 反向id==>word映射词表
reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

# get_nns_by_item基于annoy查询词最近的10个向量，返回结果是个list，里面元素是索引
for item in tc_index.get_nns_by_item(word_index[u'卖空'], 10):
    print(reverse_word_index[item])  # 用每个索引查询word

```
-----------------------------------------


## 其它参考

腾讯AI Lab开源大规模高质量中文词向量数据，800万中文词随你用 
https://mp.weixin.qq.com/s/b9NWR0F7GQLYtgGSL50gQw


语义相似度 | 我爱自然语言处理  
https://www.52nlp.cn/category/%E8%AF%AD%E4%B9%89%E7%9B%B8%E4%BC%BC%E5%BA%A6

-----------------------------------------
##  数据处理


1. 数据提取

把词典中的词和向量提取出来，分别保存为keywords.txt和vetor.npy
注意：由于数据文件很大，要用边读边处理的方式。

数据目录为：
`/mnt/sda1/corpora/full`


2. 数据优化

词典总共有880多万，看了一下拆分好的词典，里面有很多词质量不高。
可以做一些过滤，把质量差的词过滤掉。 
先整理了下可以过滤掉的词：
	* 纯数字
	* 带标点符号，且长度大于1的
		标点： [,;&:]
	* 重复3个以上
		例如：好好好， 天天天， 的的的
	* 纯英文
	* 中文+标点符号
	* 英文+标点
	保留：
	* 纯中文无标点
	* 中文+标点

### 过滤纯数字，英文符号等

```
root@ubuntu:/mnt/sda1/corpora# python dataprocess.py
开始转换向量,请稍等...
总记录数:8824330
第8824331     行[100.00%]: 三肖中特                             试
转换完成, 处理8824331行，过滤114582行，输出8709749行。
```
数据保存目录为： `/mnt/sda1/corpora/filter`


### 过滤掉全英文以及带中文标点的词：

```
root@ubuntu:/mnt/sda1/corpora# python dataprocess.py
开始转换向量,请稍等...
总记录数:8824330
[进度:100.00% 已过滤:772544] 第8824331行: 三肖中特
转换完成, 处理8824331行，过滤772544行，输出8051787行。
```
数据保存目录为： `/mnt/sda1/corpora/filter01`


### 词库向量搜索

向量搜索服务使用faiss的`VecSearch_faiss_server.py`
稍加改造，增加了按索引号提取向量的功能；

```
cd /mnt/sda1/transdat/sentence-similarity/vector_server
python VecSearch_faiss_server.py --npy=/mnt/sda1/transdat/simbert/npy/auto_service_questions.npy
```

实时搜索命令行启动, 在win下也可以使用：

```
python online_search.py --datfile=F:\project\sentence-similarity\sentence-similarity\input\auto_service_questions.txt
```



运行结果如下：

```
17:11:12.17|F:>python online_search.py --datfile=F:\project\sentence-similarity\sentence-similarity\input\auto_service_q
uestions.txt
正在加载数据，请稍候...
[2020-09-10 17:11:13,262]INFO Used Memory: 41.164 MB
----------------------------------------
请输入词语(用"|"分隔,Q退出):19
[2020-09-10 17:11:16,974]INFO 句子: 首保收费吗
[2020-09-10 17:11:17,197]INFO [[0.9999999, 0.9764246, 0.896407, 0.8947532, 0.88296264], [19, 20, 16, 2, 8]]
[2020-09-10 17:11:17,200]INFO ------------------返回结果------------------
首保收费吗
首保是否收费
首次保养是否收费
首保免费吗？
首保是否免费？
[2020-09-10 17:11:17,211]INFO [整体用时:237.50 毫秒]
----------------------------------------
请输入词语(用"|"分隔,Q退出):19|23
[2020-09-10 17:11:21,087]INFO 句子: 首保收费吗
[2020-09-10 17:11:21,090]INFO 句子2: 首保收费吗
相似度: 0.741790
[2020-09-10 17:11:21,120]INFO [整体用时:33.00 毫秒]
----------------------------------------
请输入词语(用"|"分隔,Q退出):38
[2020-09-10 17:11:27,741]INFO 句子: 有的现车吗？
[2020-09-10 17:11:27,956]INFO [[1.0000002, 0.97992516, 0.9200418, 0.83497596, 0.8289485], [38, 29, 41, 42, 44]]
[2020-09-10 17:11:27,958]INFO ------------------返回结果------------------
有的现车吗？
有现车吗？
还有现车吗？
哪个店有现车？
有没有现车可以买
[2020-09-10 17:11:27,967]INFO [整体用时:226.00 毫秒]
----------------------------------------
请输入词语(用"|"分隔,Q退出):q
```

### 测试腾讯词向量

词向量文件目录：
/mnt/sda1/transdat/sentence-similarity/vector_server

生成一个10W向量的小文件
```
16:15:52.60|F:>python dataprocess.py -outpath=./top10w -dofilter=0 -topn=100000
运行参数: Namespace(datfile='./dat/Tencent_AILab_ChineseEmbedding.txt', dofilter=True, outpath='./top10w', topn=100000)
开始转换向量,请稍等...
总记录数:8824330
[进度: 1.13% 已过滤: 2884] 第99999  行: 尤甚
正在保存字典文件...
正在保存向量文件...
转换完成, 处理100000行，过滤2884行，输出97116行。
```

生成5W个向量的小文本：

```
16:28:14.96|F:>python dataprocess.py -outpath=./top5w -dofilter=0 -topn=50000
运行参数: Namespace(datfile='./dat/Tencent_AILab_ChineseEmbedding.txt', dofilter=0, outpath='./top5w', topn=50000)
开始转换向量,请稍等...
总记录数:8824330
[进度: 0.57% 已过滤:    0] 第49999  行: 更好吃
正在保存字典文件...
正在保存向量文件...
转换完成, 处理50000行，过滤0行，输出50000行。
```

先尝试使用10W向量小词库：

词库目录：
/mnt/sda1/transdat/sentence-similarity/tx_vector/top10w

使用最新的向量搜索服务端进行测试：

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

浏览器接口调试返回结果：
```
{
"index": "[11986, 10179]",
"result": "OK",
"simcos": "0.8312157",
"words": "午餐|午饭"
}
```


加载完整词向量880万进行测试：

```
cd /mnt/sda1/transdat/sentence-similarity/vector_server
python VecSearch_faiss_server.py \
	-npy='/mnt/sda1/corpora/TX_embeding/full/vector.npy' \
	-datfile='/mnt/sda1/corpora/TX_embeding/full/keywords.txt'

```


运行结果：
```
hexi@ubuntu:/mnt/sda1/transdat/sentence-similarity/vector_server$ python VecSearch_faiss_server.py \
> -npy='/mnt/sda1/corpora/TX_embeding/full/vector.npy' \
> -datfile='/mnt/sda1/corpora/TX_embeding/full/keywords.txt'
[2020-09-16 15:36:36,720]INFO ----------faiss向量搜索服务端 v1.0.0-----------
[2020-09-16 15:36:36,720]INFO 正在加载数据文件...
[2020-09-16 15:36:38,964]INFO 加载数据文件完成: /mnt/sda1/corpora/TX_embeding/full/keywords.txt
[2020-09-16 15:36:38,964]INFO 正在加载向量并创建索引器...
[2020-09-16 15:38:15,056]INFO 向量文件:/mnt/sda1/corpora/TX_embeding/full/vector.npy
[2020-09-16 15:38:15,056]INFO 数据量:8824330, 向量维度:200
[2020-09-16 15:38:15,056]INFO 距离计算方法:INNER_PRODUCT
[2020-09-16 15:38:15,056]INFO 监听端口:7800
[2020-09-16 15:38:39,345]INFO 索引创建完成，用时:120.380154秒
[2020-09-16 15:38:39,346]INFO Used Memory: 28899.219 MB
[2020-09-16 15:38:39,356]INFO Running under Linux...
[2020-09-16 15:38:44,213]INFO 查询结果:{'values': '[[0.99999994, 0.8642118, 0.85482365, 0.8477413, 0.83343184, 0.82005787, 0.81033194, 0.8090309, 0.8070778, 0.79821426], [3936, 36725, 124531, 18424, 39477, 157901, 14563, 175403, 1111341, 66273]]', 'txt': "['快递', '快件', '快递包裹', '快递员', '快递小哥', '收快递', '快递公司', '寄件', '网购快递', '送快递']", 'result': 'OK'}
[2020-09-16 15:38:44,213]INFO 查询用时:231.65 毫秒
192.168.40.11 - - [2020-09-16 15:38:44] "POST /api/v0.1/query HTTP/1.1" 200 581 0.370721

```

查询结果：

```
{
"result": "OK",
"txt": "['给力', '很给力', '相当给力', '非常给力', '不给力', '太给力', '太给力了', '超给力', '值得称赞', '值得期待']",
"values": "[[1.0000002, 0.7813885, 0.7660224, 0.7618248, 0.7495235, 0.7280594, 0.6657632, 0.6615418, 0.6447695, 0.6371398], [9884, 37885, 136853, 104740, 27190, 237470, 133957, 308094, 75838, 18188]]"
}
```



