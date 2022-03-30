import csv
import json
import random
import requests
from lxml import etree
import re
import time
import os


def get_comment(word, user='admin'):
    # 返回评论最大页数,score这一项，好评为3，中评为2，差评为1,默认为0
    def get_page(score=0):
        temp = "&score={}&sortType=5&page=1".format(score)
        temp = base + first + temp + last
        page_data = requests.get(temp, headers=headers).text
        # print(page_data)

        return json.loads(page_data.lstrip('fetchJSON_comment98(').rstrip(');'))['maxPage']

    # 通过json获取评论
    def get_json(Url):
        data_list = []
        try:
            data = requests.get(Url, headers=headers).text
            time.sleep(random.random())
            # 将Str数据改为字典，必须去掉最开头和最结尾后面对应的符号才可以转化为字典！
            jd = json.loads(data.lstrip('fetchJSON_comment98(').rstrip(');'))

            # 取出用户评论，但是还包含了用户ID等其他信息和奇怪的符号
            com_list = jd['comments']
            # print(com_list)
            # 爬取的数据为字典，将评论按键值对取出
            for li in com_list:
                data_list.append(re.sub('[\s+]', '。', li['content']))

            # 数据写入csv
            write_csv(data_list)
            # print(data_list)
            # raise

        except Exception as e:
            print(e)
            raise

    # 数据写入csv
    def write_csv(word1):
        file = open(fp, 'a', newline='')
        fieldnames = ['comment']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        for da in word1:
            writer.writerow({'comment': da})
        file.close()

    # 写表头数据
    def write_head(word2):
        file = open(fp, 'a', newline='')
        writer = csv.writer(file)
        writer .writerow([word2])
        file.close()

    user_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
        'Opera/8.0 (Windows NT 5.1; U; en)',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) ',
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"
    ]
    headers = {
        'User_Agent': str(random.choice(user_agents)),
        'Referer': 'https://item.jd.com/100009177424.html'
    }
    # 1 success 2 fail

    # 对商品评论数据爬取
    shop_id = ''.join(list(filter(str.isdigit, word)))
    # print(shop_id)

    # 评论的json数据
    base = "https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98"
    first = "&productId={}".format(shop_id)
    last = "&pageSize=10&isShadowSku=0&fold=1"

    page_lists = [get_page(1), get_page(2), get_page(3)]
    print(page_lists)

    # 爬取时清除上次记录
    fp = 'static/data/spider_{}.csv'.format(user)
    # fp = '../static/data/spider_{}.csv'.format(user)
    if os.path.exists(fp):  # 如果文件存在
        # 删除文件，可使用以下两种方法。
        os.remove(fp)

    try:

        write_head('comment')
        # 遍历三种评价
        for pos in range(1, 4):
            middle1 = "&score={}&sortType=5".format(pos)

            # 根据页数判断循环
            print("type" + str(pos))
            if page_lists[pos - 1] < 50:
                for i in range(0, page_lists[pos - 1]):
                    # print("page" + str(i))
                    middle2 = "&page={}".format(i)
                    url = base + first + middle1 + middle2 + last
                    get_json(url)
            else:
                for i in range(0, 50):
                    # print("page" + str(i))
                    middle2 = "&page={}".format(i)
                    url = base + first + middle1 + middle2 + last
                    get_json(url)
            time.sleep(1)

        return 1
    except Exception as e:
        print(e)
        return 2


if __name__ == "__main__":
    # tar = 'https://item.jd.com/100009077475.html'
    user = 'admin'
    tar = 'https://item.jd.com/100026819200.html'
    res = get_comment(tar, user)
    print(res)
