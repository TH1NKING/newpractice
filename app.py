from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)


app.secret_key = 'baiwenchen'# 密钥

# 数据库连接函数
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',      # MySQL主机
        user='root',           # 用户名
        password='20041224cbW',  # 密码
        database='book_management'  # 数据库名
    )
    return conn

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
            return redirect(url_for('login'))

    return render_template('login.html')

# 书籍管理页面
@app.route('/book_management')
def book_management():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取用户信息
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    
    # 获取用户书籍
    cursor.execute('SELECT * FROM books WHERE user_id = %s', (user_id,))
    books = cursor.fetchall()
    conn.close()
    
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
        
        return redirect(url_for('book_management'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('edit_user.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
