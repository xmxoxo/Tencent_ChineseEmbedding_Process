#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

# TX中文词向量数据处理
import os
import sys
import numpy as np
import argparse

#import gensim
#from gensim.models import KeyedVectors


'''
数据转换，把向量库转存为单独的文件分别保存
词典文件 keywords.txt 和
向量文件 vector.npy
'''
def datprocess(filename, encoding='utf-8', outpath='./', dofilter=0, topn=0):
    try:
        i, f, total = 0, 0, 0
        chars, vectors = [], []
        print('开始转换向量,请稍等...')

        for line in open(filename, "r", encoding=encoding):
            i += 1
            # 跳过第1行
            if i==1:
                total = int(line.split(' ')[0])
                print('总记录数:%d' % total)
                continue;
            
            x = line.split(' ')
            # -----------------------------------------
            # 在这里对词语进行过滤
            if dofilter:
                if wordfilter(x[0]):
                    f +=1 # 记录被过滤掉多少行
                    #print('\n第%d行,被过滤：%s' % (i, x[0]))
                    continue;
            # -----------------------------------------
            
            chars.append(x[0])
            v = [float(i) for i in x[1:]]
            vectors.append(v)
            if i % 500:
                print('\r[进度:%5.2f%% 已过滤:%5d] 第%-7d行: %-20s' % ((i*100/total), f, i, x[0][:18]) , end='' )
            #print(x[0], v[:10])
            if topn>0:
                if i >= topn:break;

        # 自动创建目录
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        
        print()
        # 保存字典
        print('正在保存字典文件...')
        savetofile('\n'.join(chars), os.path.join(outpath, 'keywords.txt'))
        # 保存向量
        print('正在保存向量文件...')
        np.save(os.path.join(outpath, 'vector.npy'), np.array(vectors))
        print('转换完成, 处理%d行，过滤%d行，输出%d行。' % (i, f, i-f) )
    
    except Exception as e:
        print(e)
        return None

# 读入文件
def readtxtfile(fname, encoding='utf-8'):
    try:
        with open(fname, 'r', encoding=encoding) as f:  
            data=f.read()
        return data
    except Exception as e:
        return ''
    

# 保存文本信息到文件
def savetofile(txt, filename, encoding='utf-8'):
    pass
    try:
        with open(filename,'w', encoding=encoding) as f:  
            f.write(str(txt))
        return 1
    except :
        return 0

# 词典数据分析
def key_analyze ():
    # 加载数据
    filename = 'keywords.txt'
    #txt = readtxtfile(filename)
    dat = readtxtfile(filename).splitlines()
    # 计算长度
    #lstLength = [len(x) fo r x in dat]
    lstLength = map(len, dat)


# 按字典进行批量替换
def replace_dict (txt, dictKey, isreg=0):
    import re
    for k,v in dictKey.items():
        if isreg:
            txt = re.sub(k, v, txt)
        else:
            txt = txt.replace(k,v)
    return txt

# 正则表达式批量判断
# TF=0 表示任意一个不匹配就返回 True
# TF=1 表示任意一个匹配了就返回 True
def IsMatch (txt, lstKey, tf=1):
    import re
    r = None
    ret = False
    for k in lstKey:
        r = re.match(k,txt, re.U|re.I)
        # bool(r) = True 表示不匹配
        #if bool(r) != tf: 
        #if (tf & (not bool(r))) or (not tf and bool(r)):
        if (tf==1 and r!=None) or (tf==0 and r==None):
            ret = True
            break
    return ret

# 过滤
def wordfilter (txt):
    '''
    以下过滤：
	* 纯数字
	* 带英文标点符号，且长度大于1的
		标点： [,;&:]
	* 重复3个以上
		例如：好好好， 天天天， 的的的
	* 纯英文
    * 英文字母+英文标点
    * 中文标点： [。,、“”？！：.（）~?-……)(/]
    '''
    lstKey = [
            r'^\d+$',               # 纯数字
            r'^.+[\-\.,;&:\'].*$',      # 带英文标点符号，且长度大于1的
            r'^(.)\1{2,}$',           # 重复3个以上
            r'^([a-z])+$',                # 纯英文字母
            r'^([a-z])[a-z\-\.,;&:]+$',   # 英文字母+英文标点
            r'^.+[。、“”？！：（）~\?\-……)(/].*$', # 带中文标点的
            ]
    ret = IsMatch(txt, lstKey, tf=1)

    return ret


def test ():
    '''
    '''
    t = '涉及到哪些'
    t = '23434'
    t = 'strong'
    t = 'jadfjdk-,1'

    k = [r'^\d+$']
    #print(IsMatch(t, k, tf=1))
    #print(IsMatch(t, k, tf=0))

    print(wordfilter(t))
    
def main ():
    pass
    deffile='./dat/Tencent_AILab_ChineseEmbedding.txt'
    parser = argparse.ArgumentParser(description='腾讯词向量提取工具')
    parser.add_argument('-datfile', default=deffile, type=str, help='数据文件名')
    parser.add_argument('-outpath', default='./', type=str, help='输出目录')
    parser.add_argument('-dofilter', default=0, type=int, help='是否过滤非中文，默认=0不过滤')
    parser.add_argument('-topn', default=0, type=int, help='截取前N个向量,默认=0不截取')
    args = parser.parse_args()
    datfile = args.datfile
    outpath = args.outpath
    dofilter = args.dofilter
    topn = args.topn
    print('运行参数:', args)

    datprocess(filename=datfile, outpath=outpath, dofilter=dofilter, topn=topn)
    

if __name__ == '__main__':
    pass
    main()
