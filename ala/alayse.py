import pkuseg
from gensim.models import KeyedVectors
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge

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

    ala1, ana_text = sentiment(now_data, neg, pos, words)
    w2csv(ana_text)
    print(ala1)
    return ala1


if __name__ == "__main__":
    # pre_word = before_word('../static/data/analysis.csv')
    pre_word = ['外观', '速度', '效果', '充电器', '手感', '音效', '屏幕', '电池', '系统',
                '时间', '大气', '感觉', '游戏', '质感', '国货', '信号']

    # pre_pmi, use_pmi = get_pmi("手机", pre_word)
    pre_pmi = {'系统': 1.0, '电池': 1.0, '游戏': 1.0, '时间': 1.0, '屏幕': 1.0,
               '充电器': 1.0, '效果': 0.295, '外观': 0.242, '速度': 0.221, '感觉': 0.179,
               '音效': 0.0269, '手感': 0.00779, '质感': 0.00316, '大气': 1.4e-07}
    use_pmi = [('系统', 1.0), ('电池', 1.0), ('游戏', 1.0), ('时间', 1.0), ('屏幕', 1.0),
               ('充电器', 1.0), ('信号', 1.0), ('效果', 0.295), ('外观', 0.242), ('速度', 0.221), ('感觉', 0.179),
               ('音效', 0.0269), ('手感', 0.00779), ('质感', 0.00316), ('国货', 1.9e-07), ('大气', 1.4e-07)]

    # after_word = filter_word(pre_pmi)
    after_word = ['系统', '电池', '游戏', '充电器', '外观', '速度']

    # use_pmi = del_pmi(after_word, use_pmi)
    use_pmi = [('速度', 0.221), ('外观', 0.242), ('充电器', 1.0), ('游戏', 1.0), ('电池', 1.0), ('系统', 1.0)]

    # final_word = many2one(use_pmi)
    final_word = {'系统': ['系统'], '电池': ['电池'], '游戏': ['游戏'], '充电器': ['充电器'], '外观': ['外观'], '速度': ['速度']}

    score1 = analysis1(final_word, '../static/data/analysis.csv')
