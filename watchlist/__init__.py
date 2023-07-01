import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'


@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)


@app.context_processor
def inject_function():
    # 定义要引入的函数

    # 判断是否为中文字符
    def is_chinese(char):
        if '\u4e00' <= char <= '\u9fa5':
            return True
        else:
            return False

    # 判断是否包含中文字符
    def contains_chinese(text):
        for char in text:
            if is_chinese(char):
                return True
        return False

    return {
        'contains_chinese': contains_chinese
    }


from watchlist import views, errors, commands