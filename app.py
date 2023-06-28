from flask import Flask, render_template, redirect, url_for
from markupsafe import escape


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Welcome to My Watchlist!'


@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'


@app.route('/test')
def test_url_for():
    # 下面是一些调用示例
    print(url_for('hello'))
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))
    print(url_for('test_url_for'))

    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到URL后面
    print(url_for('test_url_for', num=2))
    return 'Test page'


if __name__ == '__main__':
    app.run(debug=True)

