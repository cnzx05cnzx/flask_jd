import json
import os
import pandas as pd
import time
from flask import Blueprint, request, render_template, send_from_directory, abort
from utils.sql import SQLHelper

fi = Blueprint('fi', __name__)


# 上传csv文件写入数据库
@fi.route('/upload/', methods=['POST', 'GET'], strict_slashes=False)
def api_upload():
    if request.method == 'GET':
        return render_template('web/up.html')
    else:
        # 获取信息
        # pstate状态，ptime当前时间戳

        # pstate = request.form.get('pstate')
        pstate = '1'
        ptime = time.time()

        try:
            sql = 'INSERT INTO `myweb`.`predit`(`ptime`,`pstate`)VALUES(%s,%s);'
            SQLHelper.insert2(sql, [ptime, pstate])
            # return redirect('/index')重定向
            # return render_template('')页面跳转
            return "上传成功"
        except:
            return "上传失败"


# 查询单个识别信息
@fi.route('/info/', methods=['GET', 'POST'])
def info():
    if request.method == 'GET':
        return render_template('web/info.html')
    else:
        # 获取json数据
        ptime = request.form.get('ptime')

        sql = 'select * FROM predit WHERE ptime=%s '

        try:
            res = SQLHelper.feach_one(sql, [ptime])
            print(res)
            return "查询成功"
        except:
            return "查询失败"


# 删除指定识别信息
@fi.route('/del/', methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        return render_template('web/del.html')
    else:
        # 获取json数据
        ptime = request.form.get('ptime')

        sql = 'DELETE FROM predit WHERE ptime=%s '
        try:
            res = SQLHelper.delete(sql, [ptime])
            return "删除成功"
        except:
            return "删除失败"


# 删除指定识别信息
@fi.route('/update/', methods=['GET', 'POST'])
def update():
    if request.method == 'GET':
        return render_template('web/update.html')
    else:
        # 获取json数据
        ptime = request.form.get('ptime')
        pstate = request.form.get('pstate')
        sql = 'UPDATE predit SET pstate =%s WHERE ptime=%s;'
        try:
            res = SQLHelper.update(sql, [pstate, ptime])
            return "更新成功"
        except:
            return "更新失败"


# 接受需要分析的数据文件
@fi.route('/analysis/', methods=['POST'], strict_slashes=False)
def analysis():
    data = {
        'code': '200'
    }
    return_dict = {'data': data}
    BASE_DIR = 'static/data/'
    try:
        obj = request.files.get("file")
        obj.save(os.path.join(BASE_DIR, 'analysis.csv'))

    except Exception as e:
        data['code'] = '500'
    return json.dumps(return_dict, ensure_ascii=False)
