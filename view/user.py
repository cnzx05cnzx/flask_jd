import time

from flask import Blueprint, session, redirect, request, render_template, send_from_directory
from utils.sql import SQLHelper
import re
import json

us = Blueprint('us', __name__)

User_Lists = {
    '1': {'name': 'cnzx', 'money': 15},
    '2': {'name': 'json', 'money': 151},
    '3': {'name': 'ark', 'money': 19},
    '4': {'name': 'python', 'money': 25},
}


@us.route('/index/')
def index():
    user = session.get('user')
    if user:
        return render_template('web/index.html', user=user, user_lists=User_Lists)
    else:
        return redirect('/login')


# 接收文件，返回状态
@us.route('/spider/', methods=['POST'])
def spider():
    data = {
        'code': '200'
    }
    return_dict = {'data': data}

    tar = request.args.get('tar')
    user = request.args.get('user')
    pattern = re.compile('^https://item.jd.com/[0-9]+.html$')
    if pattern.search(tar):
        user = 'admin'
        fp = 'spider_{}.csv'.format(user)
        # 无法异步,暂且用现成文件
        # res = get_comment(tar, user)

        print('send file')
        return send_from_directory('static/data/', fp, mimetype='text/csv',as_attachment=True)
    else:
        data['code'] = '500'

    return json.dumps(return_dict, ensure_ascii=False)


# 文件下载
@us.route('/download/', methods=['POST'])
def download():
    # fp = 'spider_admin.csv'
    fp = request.args.get('fp')
    print('send file')
    return send_from_directory('static/data/', fp, as_attachment=True)
