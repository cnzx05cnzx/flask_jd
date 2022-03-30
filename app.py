from flask import Flask
from view import file, account, user
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
import time

executor = ThreadPoolExecutor(2)
app = Flask(__name__)
CORS(app, resource=r'/*')

# 蓝图注册
app.register_blueprint(file.fi)
app.register_blueprint(account.ac)
app.register_blueprint(user.us)


# 热更新
# app.jinja_env.auto_reload = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True

#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'



if __name__ == '__main__':
    app.run()
