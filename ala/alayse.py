import pkuseg
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
import torch
from torchtext.legacy.data import BucketIterator, Field, TabularDataset
from ala.lstm import LSTM
from ala.use import *


# 获取候补属性集
def before_word(path):
    seg = pkuseg.pkuseg(postag=True)

    pre_data = pd.read_csv(path, encoding="utf-8")
    data = pd.DataFrame(pre_data)

    pre_words = []
    for index, row in data.iterrows():
        sentence = row['comment']
        if len(sentence) < 175:
            temp = depend_word(sentence, seg)
            if temp:
                pre_words.extend(temp)

    pre_words = counter_words(pre_words)
    ress = []
    stop_words = ['问题', '客服', '苹果', '小米', '华为', '三星', '内容', '用户', '手机']
    for index, row in pre_words.iterrows():
        if index not in stop_words:
            ress.append(index)
        if len(ress) >= 20:
            break
    print(ress)
    return ress


# 计算候补属性集pmi，用于后续过滤
def get_pmi(word, words):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth', 100)

    # 设置无界面模式，也可以添加其它设置
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    # edge_options.add_argument('headless')
    edge_options.add_argument('blink-settings=imagesEnabled=false')
    edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    edge_options.add_experimental_option('useAutomationExtension', False)

    driver = Edge(options=edge_options, executable_path='../static/addition/MicrosoftWebDriver.exe')
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                           {'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefind})'})
    driver.get('https://www.baidu.com')

    # 阈值定在0.0003以上
    ress = {}
    w_pmi = get_pmi1(word, driver)
    for w in words:
        # w1 = w + word
        w2 = word + w
        # t1 = get_pmi1(w1) + get_pmi1(w2)
        t1 = get_pmi1(w2, driver)
        t2 = get_pmi1(w, driver)
        temp = 100000000.0 * t1 / (w_pmi * t2)
        ress[w] = temp
        time.sleep(1)
        # print(temp)
    # 排序后重新转成字典
    ress = sorted(ress.items(), key=lambda kv: (kv[1], kv[0]))[::-1]
    temp = {}
    for r in ress:
        temp[r[0]] = r[1]
    print(temp, ress)
    driver.close()
    return temp, ress


# pmi与余弦相似度过滤
def filter_word(words):
    wv = KeyedVectors.load("../static/addition/wv.wordvectors", mmap='r')
    ress = []
    for w in words:
        # print(w)
        # print(wv.similarity(w, "手机"))
        if wv.similarity(w, "手机") > -0.03 and words[w] > 0.2:
            ress.append(w)
    print(ress)
    return ress


# 属性词融合
def many2one(words):
    wv = KeyedVectors.load("../static/addition/wv.wordvectors", mmap='r')
    # words = ['手机', '音效', '电池', '系统', '屏幕', '速度']

    words = words[::-1]
    res = {}
    for step, w in enumerate(words):
        res[w[0]] = step + 1

    len_w = len(words)
    for i in range(len_w):
        for j in range(i + 1, len_w):
            if wv.similarity(words[i][0], words[j][0]) >= 0.7:
                res[words[j][0]] = res[words[i][0]]

    temp = {}
    pos = {}
    for item in res.items():
        if item[1] not in pos:
            pos[item[1]] = 1
            temp[item[0]] = []

        temp[find_key(item[1], res)].append(item[0])
    print(temp)
    return temp


def analysis1(words, path):
    seg = pkuseg.pkuseg()
    # 训练数据
    now_data = pd.read_csv(path, encoding="utf-8")
    now_data = splice_word(now_data, seg)

    # 情感词典
    pos = read_file('../static/addition/postive.txt')
    neg = read_file('../static/addition/negtive.txt')

    # 抽取属性集

    ana_text = {}
    for item in words.items():
        ana_text[item[0]] = []

    ala1, ana_text, word_com = sentiment(now_data, neg, pos, words)
    w2csv(ana_text)
    print(ala1)
    print(word_com)
    return ala1, word_com


def analysis2(words):
    def tokenizer(text):
        return seg.cut(text)

    def predict(word):
        test = TabularDataset(
            path='../static/data/{}.csv'.format(word), format='csv',
            fields=FIELD2, skip_header=True)

        test_iter = BucketIterator(
            test,
            batch_size=batch_size,
            sort_key=lambda x: len(x.content),
            sort_within_batch=False,
            repeat=False
        )
        cnt = 0
        for i, batch in enumerate(test_iter):
            model.train()
            content = batch.content

            pred = model(content)
            cnt += sum(torch.argmax(pred, dim=1).numpy())
        score = ((2 * cnt - len(test)) / len(test) + 1) * 2.5
        # print("%s: %.2f" % (word, score))
        return score

    batch_size = 32
    seg = pkuseg.pkuseg()

    TEXT = Field(sequential=True, tokenize=tokenizer, fix_length=125)
    LABEL = Field(sequential=False, use_vocab=False)

    FIELD1 = [('label', LABEL), ('content', TEXT)]
    FIELD2 = [('content', TEXT)]

    df = TabularDataset(
        path='../static/data/phone.csv', format='csv',
        fields=FIELD1, skip_header=True)

    TEXT.build_vocab(df, min_freq=3, vectors='glove.6B.50d')

    model = LSTM(len(TEXT.vocab), 64, 128)
    model.load_state_dict(torch.load('../static/model/torchtext.pkl'))

    ress = {}
    for item in words.items():
        ress[item[0]] = predict(item[0])
    print(ress)
    return ress


if __name__ == "__main__":
    # pre_word = before_word('../static/data/analysis.csv')
    pre_word = ['外观', '速度', '效果', '充电器', '手感', '音效', '屏幕', '电池', '系统',
                '时间', '大气', '感觉', '游戏', '质感', '国货', '信号']

    # pre_pmi, use_pmi = get_pmi("手机", pre_word)
    pre_pmi = {'系统': 1.0, '电池': 1.0, '游戏': 1.0, '时间': 1.0, '屏幕': 1.0,
               '充电器': 1.0, '效果': 0.295, '外观': 0.242, '速度': 0.221, '感觉': 0.179,
               '音效': 0.0269, '手感': 0.00779, '质感': 0.00316, '大气': 1.4e-07}
    # use_pmi = [('系统', 1.0), ('电池', 1.0), ('游戏', 1.0), ('时间', 1.0), ('屏幕', 1.0),
    #            ('充电器', 1.0), ('信号', 1.0), ('效果', 0.295), ('外观', 0.242), ('速度', 0.221), ('感觉', 0.179),
    #            ('音效', 0.0269), ('手感', 0.00779), ('质感', 0.00316), ('国货', 1.9e-07), ('大气', 1.4e-07)]

    # after_word = filter_word(pre_pmi)
    after_word = ['系统', '电池', '游戏', '充电器', '外观', '速度']

    # use_pmi = del_pmi(after_word, use_pmi)
    use_pmi = [('速度', 0.221), ('外观', 0.242), ('充电器', 1.0), ('游戏', 1.0), ('电池', 1.0), ('系统', 1.0)]

    # final_word = many2one(use_pmi)
    # words_cos = get_cos(final_word)
    final_word = {'系统': ['系统'], '电池': ['电池'], '游戏': ['游戏'], '充电器': ['充电器'], '外观': ['外观'], '速度': ['速度']}
    words_cos = [[1.0, 0.19, 0.27, -0.06, 0.04, 0.24, 0.3], [0.19, 1.0, 0.26, 0.14, -0.02, 0.17, 0.09],
                 [0.27, 0.26, 1.0, -0.05, -0.05, 0.39, 0.06], [-0.06, 0.14, -0.05, 1.0, -0.29, -0.04, 0.16],
                 [0.04, -0.02, -0.05, -0.29, 1.0, 0.12, 0.11], [0.24, 0.17, 0.39, -0.04, 0.12, 1.0, 0.03],
                 [0.3, 0.09, 0.06, 0.16, 0.11, 0.03, 1.0]]

    # score1, comments = analysis1(final_word, '../static/data/analysis.csv')
    # score2 = analysis2(final_word)
    # score = all_score(score1, score2)
    # words_pie = get_pie(comments)
    comments = {'系统': [46, 75], '电池': [43, 13], '游戏': [49, 9], '充电器': [0, 100], '外观': [183, 0], '速度': [164, 13]}
    score = {'系统': 2.75, '电池': 1.69, '游戏': 1.98, '充电器': 1.36, '外观': 3.87, '速度': 2.02}
    words_pie = {'系统': 0.17, '电池': 0.08, '游戏': 0.08, '充电器': 0.14, '外观': 0.26, '速度': 0.25}
