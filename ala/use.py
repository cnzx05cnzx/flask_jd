import csv
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
import pandas as pd
import re

# 使用依存句法分析获取候补频繁项集
from gensim.models import KeyedVectors


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
    g = corpus.groupby(['word']).agg({'cnt': 'count'}).sort_values('cnt', ascending=False)
    return g


# 依存语法分析
def depend_word(TEXT, seg):
    # 接口地址
    url = "http://ltpapi.xfyun.cn/v1/dp"
    # 开放平台应用ID
    x_appid = "cdeb9932"
    # 开放平台应用接口秘钥
    api_key = "06b69c30f3d03ed837750242cb4618cd"

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
        # print(res)
    except:
        print('err')
    return res


def get_pmi1(word, driver):
    try:
        url = 'https://www.baidu.com/s?wd="{}"'.format(word)
        driver.get(url)
        t = driver.find_element_by_xpath('//*[@id="tsn_inner"]/div[2]/span').text
        t = "".join(list(filter(str.isdigit, t)))
        # print(t)
    except:
        print("err")
        t = 1
    return int(t)


def get_pmi2(word1, word2, driver):
    try:
        word = word1 + ' ' + word2
        url = 'https://www.baidu.com/s?wd="{}"'.format(word)
        driver.get(url)
        t = driver.find_element_by_xpath('//*[@id="tsn_inner"]/div[2]/span').text
        t = "".join(list(filter(str.isdigit, t)))
    # print(t)
    except:
        print("err")
        t = 20000000
    return int(t)


# 根据序号找键值
def find_key(tar, word):
    for item in word.items():
        if item[1] == tar:
            return item[0]
    return 'none'


# list遍历删除元素
def del_pmi(tar, p_list):
    for p in p_list[::-1]:
        if p[0] not in tar:
            p_list.remove(p)
    print(p_list[::-1])
    return p_list[::-1]


# 情感评分,情感词典部分
def read_file(name):
    words = list()
    with open(name, "r", encoding='utf-8') as f:  # 打开文件
        for line in f.readlines():
            line = line.rstrip('\n')
            words.append(line)
    return words


def get_stop_words():
    # 读入停用词表
    words_list = []

    with open("../static/addition/停用词.txt", 'r', encoding='UTF-8') as f:
        lines = f.readlines()
        for line in lines:
            words_list.append(line.strip())
    my_words = ["。。", "手机"]
    words_list.extend(my_words)

    return words_list


# use pkuseg splice word
def splice_word(data, seg):
    data['cut'] = data['comment'].apply(lambda x: list(seg.cut(x)))

    stop_words = get_stop_words()

    data['cut'] = data['comment'].apply(lambda x: [i for i in seg.cut(x) if i not in stop_words])
    return data


def cut_word(word):
    return re.split(r'[，。!?\s]', word)


def sentiment(words, data, neg_words, pos_words, text_li):
    ress = {}
    for d in data:
        ress[d] = 0.0

    sum = 0
    for index, row in words.iterrows():
        sum += 1
        temp = row['cut']
        w_texts = cut_word(row['comment'])

        pos = 0
        pos_t = []
        for t in temp:

            if t in data and (t not in pos_t):
                # print(t,w_texts)
                for step, x in enumerate(w_texts):
                    if t in x and len(x) > len(t):
                        # print(t, x, w_texts)
                        text_li[t].append(x)
                        break

                i = j = pos
                while i >= 0 and j < len(temp):
                    if temp[i] in neg_words:
                        if i >= 1 and temp[i - 1] == '不':
                            ress[t] += 1
                        else:
                            ress[t] -= 1

                        break
                    elif temp[i] in pos_words:
                        if i >= 1 and temp[i - 1] == '不':
                            ress[t] -= 1
                        else:
                            ress[t] += 1

                        break
                    else:
                        i -= 1
                        j += 1

                pos_t.append(t)

            pos += 1

    for (k, v) in ress.items():
        ress[k] = (1.0 * v / sum + 1) * 2.5

    print(ress)
    return ress


# 将数据写入csv
def w2csv(word):
    for item in word.items():
        fileHeader = ["review"]
        CsvFile = open("../static/data/{}.csv".format(item[0]), "w", encoding='utf-8', newline='')
        writer = csv.writer(CsvFile)

        # 写入的内容都是以列表的形式传入函数
        writer.writerow(fileHeader)
        for t in item[1]:
            # print(t)
            writer.writerow([t])
        CsvFile.close()


# 根据序号找键值
def find_word(tar, word):
    for item in word.items():
        if tar in item[1]:
            return item[0]
    return 'none'


def sentiment(words, neg_words, pos_words, wew):
    # data 所有属性   text_li 属性对应句子   ress 评分结果  comments 好坏评数量 0好 1坏
    data = []
    text_li = {}
    ress = {}
    comments = {}
    for item in wew.items():
        data.extend(item[1])
        text_li[item[0]] = []
        ress[item[0]] = 0.0
        comments[item[0]] = [0, 0]

    sum = 0
    for index, row in words.iterrows():
        sum += 1
        temp = row['cut']
        w_texts = cut_word(row['comment'])

        pos = 0
        pos_t = []
        for t in temp:

            if t in data and (t not in pos_t):
                # print(t,w_texts)
                for step, x in enumerate(w_texts):
                    if t in x and len(x) > len(t):
                        # print(t, x, w_texts)
                        text_li[find_word(t, wew)].append(x)
                        break

                i = j = pos
                while i >= 0 and j < len(temp):
                    if temp[i] in neg_words:
                        if i >= 1 and temp[i - 1] == '不':
                            ress[find_word(t, wew)] += 1
                            comments[find_word(t, wew)][0] += 1
                        else:
                            ress[find_word(t, wew)] -= 1
                            comments[find_word(t, wew)][1] += 1

                        break
                    elif temp[i] in pos_words:
                        if i >= 1 and temp[i - 1] == '不':
                            ress[find_word(t, wew)] -= 1
                            comments[find_word(t, wew)][1] += 1
                        else:
                            ress[find_word(t, wew)] += 1
                            comments[find_word(t, wew)][0] += 1
                        break
                    else:
                        i -= 1
                        j += 1

                pos_t.append(t)

            pos += 1

    for (k, v) in ress.items():
        ress[k] = (1.0 * v / sum + 1) * 2.5

    return ress, text_li, comments


# 两种分数均衡计算
def all_score(x, y):
    ress = {}
    for a, b in zip(x.items(), y.items()):
        ress[a[0]] = round(0.5 * a[1] + 0.5 * b[1], 2)
    print(ress)
    return ress


# 各属性相似度
def get_cos(words):
    wv = KeyedVectors.load("../static/addition/wv.wordvectors", mmap='r')
    words['手机'] = 1
    ress = []
    # texts = ['屏幕', '外观', '速度']
    for item in words.items():
        temp = []
        for itemm in words.items():
            temp.append(round(wv.similarity(item[0], itemm[0]), 2))
        ress.append(temp)
    print(ress)

    return ress


# 评论占比
def get_pie(words):
    summ = 0
    for item in words.items():
        summ += item[1][0] + item[1][1]
    ress = {}
    for item in words.items():
        ress[item[0]] = round(1.0 * (item[1][0] + item[1][1]) / summ, 2)
    print(ress)
    return ress
