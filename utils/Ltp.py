#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
import pkuseg
import pandas as pd
import re


# 使用依存句法分析获取候补频繁项集

def is_Chinese(word):
    for ch in word:
        if '\u4e00' > ch or ch > '\u9fff':
            return False
    return True


def judge_word(word):
    return True if word == "SBV" or word == "VOB" or word == "POB" else False


def split_sen(line):
    line_split = re.split(r'[.?!。？！]', line.strip())
    line_split = [line.strip() for line in line_split if
                  line.strip() not in ['。', '！', '？', '；', '，'] and len(line.strip()) > 1]
    return line_split


# 词频统计
def counter_words(word):
    corpus = pd.DataFrame(word, columns=['word'])
    corpus['cnt'] = 1

    # 分组统计
    g = corpus.groupby(['word']).agg({'cnt': 'count'}).sort_values('cnt', ascending=False)

    # print(g.head(20))
    return g


# 依存语法分析
def depend_word(TEXT):
    # 接口地址
    url = "http://ltpapi.xfyun.cn/v1/dp"
    # 开放平台应用ID
    x_appid = "cdeb9932"
    # 开放平台应用接口秘钥
    api_key = "06b69c30f3d03ed837750242cb4618cd"
    # 语言文本

    body = urllib.parse.urlencode({'text': TEXT}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    s = json.loads(result)

    res = []

    # api 错误代码
    if s['code'] != '0':
        # print(s)
        return res
    try:
        comlist = s['data']['dp']
        words = seg.cut(TEXT)

        if len(words) == len(comlist):
            # print('fine')
            pos = 0
            for com in comlist:
                r = com['relate']
                if words[pos][1] == 'n' and judge_word(r):
                    res.append(words[pos][0])
                pos += 1
        if res:
            for r in res[::-1]:
                if not is_Chinese(r) or not len(seg.cut(r)) == 1:
                    res.remove(r)
        print(res)
    except:
        print('err')
    return res


if __name__ == '__main__':
    seg = pkuseg.pkuseg(postag=True)

    pre_data = pd.read_csv('data/comment.csv', encoding="gbk")
    # pre_data = pd.read_csv('data/temp.csv', encoding="gbk")
    data = pd.DataFrame(pre_data)

    pre_words = []
    for index, row in data.iterrows():
        # 考虑分词精度问题
        # sentence = split_sen(row['comment'])
        # for sen in sentence:
        #     temp = depend_word(row['comment'])
        #
        #     if temp:
        #         print(temp)
        #         words.extend(temp)

        sentence = row['comment']
        if len(sentence) < 175:
            temp = depend_word(sentence)

            if temp:
                # print(temp)
                pre_words.extend(temp)

    # 打印候补频繁项集
    pd.set_option('display.max_columns', None)
    # 显示所有行
    pd.set_option('display.max_rows', None)
    # 设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth', 100)

    # 统计候补频繁项集
    print(pre_words)
    pre_words = counter_words(pre_words)
    # 使用set聚类
    once_word = set(pre_words)
    print(once_word)
    # print(pre_words)

    # 前10频率数据
    pos = 0
    for index, row in pre_words.iterrows():
        print(index)
        pos += 1
        if pos >= 10:
            break
    # res = ['速度', '效果', '外观', ' 音效', '手机', '屏幕', '时间', '手感', '游戏', '问题']
