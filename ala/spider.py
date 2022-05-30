import csv
import json
import requests
import re
import time


# 获取评论数据的页数
def get_page(Url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'referer': 'https://item.jd.com/100007299145.html',
    }

    data = requests.get(Url, headers=headers).text
    time.sleep(2)

    try:
        jd = json.loads(data.lstrip('fetchJSON_comment98(').rstrip(');'))

        page = jd['maxPage']
        return page
    except:
        print('err')
        return 1


# 通过json获取评论
def get_json(Url):
    data_list = []
    headers = {
        # 用的哪个浏览器
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'referer': 'https://item.jd.com/100007299145.html',
    }

    data = requests.get(Url, headers=headers).text
    time.sleep(2)

    # 将Str数据改为字典，必须去掉最开头和最结尾后面对应的符号才可以转化为字典！
    try:
        jd = json.loads(data.lstrip('fetchJSON_comment98(').rstrip(');'))

        # 取出用户评论，但是还包含了用户ID等其他信息和奇怪的符号
        com_list = jd['comments']
        # com_sum = jd['productCommentSummary']['commentCountStr']

        for li in com_list:
            data_list.append(re.sub('[\s+]', '。', li['content']))

        write_csv(data_list)

    except:
        print(Url)
        return


# 数据写入csv
def write_csv(data):
    file = open('../static/data/spider_admin.csv', 'a+', newline='')
    fieldnames = ['comment']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    for da in data:
        writer.writerow({'comment': da})
    file.close()


def get_select_cor(word):
    sid = word.split('/')[-1][:-5]

    cnt = 0
    base = "https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98"
    first = "&productId={}".format(sid)
    last = "&pageSize=10&isShadowSku=0&fold=1"
    middle = "&score=0&sortType=5&page=1"
    fin = base + first + middle + last
    sum = get_page(fin)

    # 1 21
    print("all page is %s" % sum)
    for i in range(1, sum + 1):
        middle = "&score=0&sortType=5&page={}".format(i)
        fin = base + first + middle + last
        get_json(fin)
        print('finsh ' + str(cnt))
        cnt = cnt + 1
    print('complete')


if __name__ == "__main__":
    url = 'https://item.jd.com/10046082756557.html'
    get_select_cor(url)
    # 获取商品id存入list
