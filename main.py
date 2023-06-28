from flask import Flask, render_template, redirect, url_for
from markupsafe import escape


app = Flask(__name__)

# 临时用这个全局变量来存书，最后改成用数据库来存
g_books = []
g_books_file_path = 'books.txt'


@app.route('/admin')
def hello_admin():
    return 'Hello Admin'


@app.route('/guest/<guest>')
def hello_guest(guest):
    return f'Hello {guest} as Guest'


@app.route('/')
def index():
    return '<h1>Index-Page</h1><h2>Hello World!</h2>'


@app.route('/books')
def books():
    books = [
        '物理',
        '数学',
    ]
    return '<h1>{}</h1>'.format(' '.join(books))


'''
@app.route('/book/add/<name>')
def book_add(name):
    global g_books
    g_books.append(name)
    with open(g_books_file_path, 'a', encoding='utf-8') as f:
        f.write(name)
    return '<h1>书籍添加成功: {}</h1>'.format(name)
'''


@app.route('/<name>')
def hello(name):
    return f"Hello, {escape(name)}!"


'''
b站的路由设计
/video/视频id
/video/BV1YP411q7YS/
'''


@app.route('/user/<name>')
def user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest = name))


@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f"Post {post_id}"


if __name__ == '__main__':
    app.run(debug=True)

