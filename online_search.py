# !/usr/bin/env python3
# -*- coding:utf-8 _*-  
""" 
@Author: xmxoxo 
@File:  online_search.py
@Time:  2020/9/7
@Software: Editplus
@Description: 词向量查询工具
"""

#import warnings
#warnings.filterwarnings("ignore")

import argparse
import os
import sys
import requests
import json
import time
import logging
import numpy as np

from flask import Flask, request, render_template, jsonify, abort
from flask import url_for, Response

parser = argparse.ArgumentParser(description='腾讯词向量搜索工具')
parser.add_argument('-api', default='', required=True, type=str, help='服务端API') #
parser.add_argument('-topn', default=5, type=int, help='返回匹配条数')
args = parser.parse_args()

api_url = args.api

#-----------------------------------------
def MemoryUsed ():
    # 查看当前进程使用的内存情况
    import os, psutil
    process = psutil.Process(os.getpid())
    info = 'Used Memory: %.3f MB' % (process.memory_info().rss / 1024 / 1024 )
    return info
#-----------------------------------------

# 根据向量或者索引号，返回最相似的结果；
def Vector_search (vector='', topn=5, index='', txt=''):
    url=api_url+'/api/v0.1/query'
    ret = [[], []]
    try:
        dt = {'v': str(list(vector)), 'n':topn, 'i':index, 's':txt}
        res = requests.post(url, data=dt, timeout=2)
        res.encoding = 'utf-8'
        res = json.loads(res.text)
        if res['result'] == 'OK':
            values = json.loads(res["values"])
            txt = eval(res["txt"])
            ret = [(txt[i],values[0][0][i])  for i in range(len(txt))] #
        else:
            print(res)
        return ret
    except Exception as e:
        print(e)
        return ret

# 根据索引号查询句子的向量
def Vector_index (index=0, txt=''):
    url=api_url+'/api/v0.1/vector'
    ret = []
    try:
        dt = {'index': index,'txt': txt}
        res = requests.post(url, data=dt, timeout=2)
        res.encoding = 'utf-8'
        res = json.loads(res.text)
        #print(res)
        if res['result'] == 'OK':
            ret = json.loads(res["vector"])
        return ret
    except Exception as e:
        print('Error at Vector_index')
        print(e)
        return ret

# 调用接口， 计算两个词的相似度
def Vector_sim (a,b):
    url=api_url+'/api/v0.1/sim'
    ret = ''
    try:
        dt = {'words': ('%s|%s' % (a,b))}
        res = requests.post(url, data=dt, timeout=2)
        res.encoding = 'utf-8'
        res = json.loads(res.text)
        if res['result'] == 'OK':
            ret = json.loads(res["simcos"])
        return ret
    except Exception as e:
        print(e)
        return ret
    


# 实现 "国王-男人+女人=皇后" 的运算
# 传入三个词语
def Vecotr_opera (a,b,c):
    ret = []
    try:

        vec_a = np.array(Vector_index(txt=a))
        vec_b = np.array(Vector_index(txt=b))
        vec_c = np.array(Vector_index(txt=c))
        
        # 计算向量差
        vec = vec_a - vec_b + vec_c
        ret = Vector_search(vector=vec, topn=args.topn)
        # 在结果中过滤掉原结果
        ret = filter(lambda x:x[0] not in [a,b,c], ret)
        return ret
    except Exception as e:
        return ret

# 启动HTTP服务
def HTTPServer ():
    pass



# 命令行方法 
def main_cli ():
    # 显示内存使用
    logging.info(MemoryUsed())

    print('-'*40)
    print('腾讯词向量搜索工具')
    print('''可输入多个词语，词语之间用","分隔; 
输入1个词：查询相似的词；
输入2个词：查询两个词的相似度；
输入3个词：计算A-B+C,例如：国王-男人+女人=皇后
     ''')

    while 1:
        try:
            print('-'*40)
            strInput = input('请输入词语(Q退出):').strip()
        except :
            strInput = ''
        if strInput in [''] : continue
        if strInput in ['Q', 'q'] : break
        start = time.time()

        # 处理输入的单词
        strInput = strInput.strip()
        lstsent = tuple(filter(None, strInput.split("，")))[:3]
        
        if len(lstsent) == 1:
            logging.info('查询词语的近义词:%s ' % lstsent[0])
            ret = Vector_search(txt=lstsent[0], topn=args.topn)
            if ret:
                ret = '\n'.join( [str(x) for x in ret])
                logging.info('查询结果:\n%s' % str(ret) )
            else:
                logging.info('查询错误:%s' % str(ret) )                
        if len(lstsent) == 2:
            logging.info('查询 %s 与 %s 的相似度:' % lstsent )
            ret = Vector_sim (lstsent[0], lstsent[1])
            logging.info('相似度:%s' %  str(ret))
        if len(lstsent) == 3:
            logging.info('向量加减:%s-%s+%s' % lstsent)
            ret = Vecotr_opera (lstsent[0], lstsent[1], lstsent[2])
            if ret:
                ret = '\n'.join( [str(x) for x in ret])
                logging.info('查询结果:\n%s' % str(ret))
            else:
                logging.info('查询错误, 可能是词库未收录该词，请加载大词库。' )

        logging.info('整体用时:%.2f 毫秒' % ((time.time() - start)*1000) )

if __name__ == '__main__':
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
    
    main_cli()
