from flask import Blueprint, session, redirect, request, render_template, send_from_directory
import json

from utils.sql import SQLHelper

ac = Blueprint('ac', __name__)


@ac.route('/login', methods=['post', 'get'])
def login():
    data = request.get_json(silent=True)
    username = data["username"]
    password = data["password"]
    print(username,password)

    return_dict = {'return_code': '200', 'result': False}
    name_list = ['', 'person', 'enterprise', 'administrator']
    sql = "SELECT p_name,p_password FROM ssm.person where p_name='{}' and p_password='{}';".format(
      username, password)
    # print(sql)
    res = SQLHelper.feach_one(sql)
    if res:
        return_dict['result'] = True

    return json.dumps(return_dict, ensure_ascii=False)


@ac.route('/register', methods=['POST'])
def register():
    return_dict = {'return_code': '200', 'result': False}

    data = request.get_json(silent=True)
    username = data["username"]
    password = data["password"]

    sql = "INSERT INTO ssm.person(p_name,p_password)VALUES('{}','{}');".format(
        username, password)
    try:
        SQLHelper.insert1(sql)
        return_dict['result'] = True
    except:
        print("error")
        return_dict['return_code'] = '500'

    return json.dumps(return_dict, ensure_ascii=False)


@ac.route('/layout/')
def layout():
    del session['user']
    return redirect('/login')
