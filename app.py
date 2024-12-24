from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from math import ceil

app = Flask(__name__)
app.secret_key = 'baiwenchen'  # 密钥

# 数据库连接函数
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',      # MySQL主机
        user='root',           # 用户名
        password='20041224cbW',  # 密码
        database='book_management'  # 数据库名
    )
    return conn

PER_PAGE = 20

# 登录页面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('book_management'))
        else:
            flash('用户名或密码错误')
            return redirect(url_for('login'))

    return render_template('login.html')

# 书籍管理页面
@app.route('/book_management', methods=['GET'])
def book_management():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # 如果未登录，重定向到登录页面

    user_id = session['user_id']  # 获取当前登录用户的 ID

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 查询当前用户的信息
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return redirect(url_for('login'))  # 如果未查询到用户信息，重定向到登录页面

    # 查询当前用户的书籍列表
    cursor.execute('SELECT * FROM books WHERE user_id = %s', (user_id,))
    books = cursor.fetchall()

    conn.close()

    # 渲染模板并传递用户信息和书籍列表
    return render_template('book_management.html', user=user, books=books)

# 修改用户信息
@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        nickname = request.form['nickname']
        gender = request.form['gender']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET nickname = %s, gender = %s, password = %s WHERE id = %s',
                       (nickname, gender, password, user_id))
        conn.commit()
        conn.close()
        
        flash('用户信息已更新')
        return redirect(url_for('book_management'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('edit_user.html', user=user)

# 添加书籍页面
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        book_number = request.form['book_number']
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        description = request.form['description']
        cover_image = request.form['cover_image']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (user_id, book_number, title, author, publisher, description, cover_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, book_number, title, author, publisher, description, cover_image))
        conn.commit()
        conn.close()

        flash('书籍添加成功')
        return redirect(url_for('book_management'))

    return render_template('add_book.html')

# 修改书籍页面
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 获取书籍信息
    cursor.execute('SELECT * FROM books WHERE id = %s AND user_id = %s', (book_id, user_id))
    book = cursor.fetchone()

    if not book:
        conn.close()
        flash('未找到该书籍或您无权限修改')
        return redirect(url_for('book_management'))

    if request.method == 'POST':
        book_number = request.form['book_number']
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        description = request.form['description']
        cover_image = request.form['cover_image']

        cursor.execute('''
            UPDATE books
            SET book_number = %s, title = %s, author = %s, publisher = %s, description = %s, cover_image = %s
            WHERE id = %s AND user_id = %s
        ''', (book_number, title, author, publisher, description, cover_image, book_id, user_id))
        conn.commit()
        conn.close()

        flash('书籍修改成功')
        return redirect(url_for('book_management'))

    conn.close()
    return render_template('edit_book.html', book=book)

# 删除单本书籍
@app.route('/delete_book/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = %s AND user_id = %s', (book_id, user_id))
    conn.commit()
    conn.close()

    flash('书籍删除成功')
    return redirect(url_for('book_management'))

if __name__ == '__main__':
    app.run(debug=True)
