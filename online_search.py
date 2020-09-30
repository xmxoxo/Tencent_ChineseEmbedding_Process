# !/usr/bin/env python3
# -*- coding:utf-8 _*-  
""" 
@Author: xmxoxo 
@File:  online_search.py
@Time:  2020/9/7
@Software: Editplus
@Description: 词向量查询工具
"""

import warnings
warnings.filterwarnings("ignore")

import argparse
import os
import sys
import requests
import json
import time
import logging
import numpy as np


parser = argparse.ArgumentParser(description='命令行查询工具')
parser.add_argument('--datfile', default='', required=True, type=str, help='数据文件名') #
parser.add_argument('--topn', default=5, type=int, help='返回匹配条数')
args = parser.parse_args()
#-----------------------------------------
def MemoryUsed ():
    # 查看当前进程使用的内存情况
    import os, psutil
    process = psutil.Process(os.getpid())
    info = 'Used Memory: %.3f MB' % (process.memory_info().rss / 1024 / 1024 )
    return info

#-----------------------------------------

# 余弦距离
CosSim_dot = lambda a,b: np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 读入文件
def readtxtfile(fname,encoding='utf-8'):
    pass
    try:
        with open(fname,'r',encoding=encoding) as f:  
            data=f.read()
        return data
    except :
        return ''


# 向量搜索API
api_url = 'http://192.168.15.111:7800'

# 根据向量或者索引号，返回最相似的结果；
def Vector_search (vector, topn=5, index=None):
    url=api_url+'/api/v0.1/query'
    ret = [[], []]
    try:
        dt = {'v': str(list(vector)), 'n':topn}
        if index:
            dt['i'] = index 
        res = requests.post(url, data=dt, timeout=2)
        res.encoding = 'utf-8'
        res = json.loads(res.text)
        #print(res)
        if res['result'] == 'OK':
            ret = json.loads(res["values"])
        return ret
    except Exception as e:
        print(e)
        return ret

# 根据索引号查询句子的向量
def Vector_index (index):
    url=api_url+'/api/v0.1/vector'
    ret = []
    try:
        dt = {'index': index}
        res = requests.post(url, data=dt, timeout=2)
        res.encoding = 'utf-8'
        res = json.loads(res.text)
        if res['result'] == 'OK':
            ret = json.loads(res["vector"])
        return ret
    except Exception as e:
        print(e)
        return ret

# 加载数据文件处理成字典
def make_dict (filename):
    try:
        txts = readtxtfile(filename).splitlines()
        sentences = []
        for x in txts:
            if '\t' in x:
                sent = x.split('\t')[1]
            else:
                sent = x
            sentences.append(sent)
    except :
        sentences = None
    return sentences


# 命令行主方法 
def main_cli ():
    #################################################################################################
    # 指定日志
    logging.basicConfig(level = logging.DEBUG,
                format='[%(asctime)s] %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename= os.path.join('./', 'app.log'),
                filemode='w'
                )
    #################################################################################################
    # 定义一个StreamHandler，将 INFO 级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    #formatter = logging.Formatter('[%(asctime)s] %(filename)s [line:%(lineno)d] %(levelname)s %(message)s')
    formatter = logging.Formatter('[%(asctime)s]%(levelname)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    #################################################################################################

    # 读入数据文件并处理成字典
    print('正在加载数据，请稍候...')
    #sentences, dic_sentences = make_dict(args.datfile)
    sentences = readtxtfile(args.datfile).splitlines()
    if not sentences:
        print('加载数据失败,请检查数据文件...')
        sys.exit()

    # 显示内存使用
    logging.info(MemoryUsed())

    while 1:
        try:
            print('-'*40)
            strInput = input('请输入词语(用"|"分隔,Q退出):').strip()
        except :
            strInput = ''
        if strInput  in [''] : continue
        if strInput in ['Q', 'q'] : break
        start = time.time()

        word_a, word_b = '',''
        index_a, index_b = None, None
        if strInput.find('|')>=0:
            lstsent = strInput.split('|')[:2]
            word_a, word_b = lstsent
            # 如果是数字，就转换成索引号
            if word_a.isdigit():
                index_a = int(word_a)
                word_a = sentences[index_a]
            if word_b.isdigit():
                index_b = int(word_b)
                word_b = sentences[index_b]
        else:
            word_a = strInput
            if word_a.isdigit():
                index_a = int(word_a)
                word_a = sentences[index_a]

        logging.info('句子: %s' % word_a )
        if word_b:
            logging.info('句子2: %s' % word_a)

        # 在字典里查找词
        if not index_a:
            try:
                index_a = sentences.index(word_a)
                index_b = sentences.index(word_a)
            except :
                pass 
        
        if not index_a:
            print('词库中未到到该词...')
            continue
        
        if index_a and index_b:
            '''
            # 两个词求相似度
            vec_a = Vector_index(index_a)
            vec_b = Vector_index(index_b)
            s = CosSim_dot(vec_a, vec_b)
            '''
            # 直接使用API接口
            print('相似度: %f' % s)
        
        else:
            # 词向量搜索
            ret = Vector_search('', topn=args.topn, index=index_a)
            logging.info(ret)
            if not ret:
                print('服务端返回出错...')
                continue

            # 找到对应的句子
            ret_sent = [sentences[i] for i in ret[1]]
            logging.info( '返回结果'.center(40,'-') + '\n' + '\n'.join(ret_sent))
        
        logging.info('[整体用时:%.2f 毫秒]' % ((time.time() - start)*1000) )


if __name__ == '__main__':
    pass
    main_cli()
