from flask import Flask, render_template, flash, redirect, \
    url_for, session, logging, request, g
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
# import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'
mysql = MySQL(app)

# SQLAlchemy Config
# app.config['SQLALCHEMY_DATABASE_URI'] =


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '^6y7oaU2TkcK'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# conn = sqlite3.connect('test.db')


# def connect_db():
#     return sqlite3.connect('test.db')


# def get_posts():
#     '''Gets all posts from database'''
#     conn = sqlite3.connect('test.db')
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM posts;")
#     posts = cur.fetchall()
#     return posts

def get_posts():
    '''Connects to MySQL database'''
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts")

    posts = cur.fetchall()

    if len(posts) > 0:
        return posts
    msg = 'No posts Found'
    cur.close()


@app.route('/')
def home():
    '''returns home.html page'''
    posts = get_posts()
    if len(posts) > 0:
        return render_template('home.html', posts=posts)
    msg = 'No posts Found'
    return render_template('home.html', msg=msg)


@app.route('/about')
def about():
    '''Returns about.html'''
    return render_template('about.html')

# Leaving this incase I want to get single posts in the future

# @app.route('/post/<string:id>/')
# def grab_post(id):
#     '''Returns single post'''
#     cur = mysql.connect.cursor()
#     cur.execute("SELECT * FROM posts WHERE id = %s;", [id])
#     post = cur.fetchone()
#     return render_template('post.html', post=post)


# Keeping this in case I want to add more users

# class RegisterForm(Form):
#     name = StringField('Name', [validators.Length(min=1, max=50)])
#     username = StringField('Username', [validators.Length(min=4, max=25)])
#     email = StringField('Email', [validators.Length(min=6, max=60)])
#     password = PasswordField('Password', [
#         validators.DataRequired(),
#         validators.EqualTo('confirm', message='Passwords do not match')
#     ])
#     confirm = PasswordField('Confirm Password')

# class ContactForm(Form):
#     name = TextField("Name")
#     email = TextField("Email")
#     subject = TextField("Subject")
#     message = TextAreaField("Message")
#     submit = SubmitField("Send")


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     '''Register new user'''
#     form = RegisterForm(request.form)
#     if request.method == 'POST' and form.validate():
#         name = form.name.data
#         email = form.email.data
#         username = form.username.data
#         password = sha256_crypt.encrypt(str(form.password.data))
#         cur = mysql.connect.cursor()
#         cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
#                     (name, email, username, password))
#         mysql.connect.commit()
#         cur.close()
#         flash('You are registered and can login.', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        conn = sqlite3.connect('test.db')
        cur = conn.cursor()
        result = cur.execute(
            "SELECT * FROM users WHERE username = (?)", ('mclaughlin14',))
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials. Try again.'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM posts;")
    posts = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', posts=posts)
    msg = 'No Posts Found'
    return render_template('dashboard.html', msg=msg)
    cur.close()


class PostForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])


@is_logged_in
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        post_title = form.title.data

        body = form.body.data
        cur = sqlite3.connect.cursor()

        cur.execute('INSERT INTO posts(title, body, author) VALUES(%s, %s, %s)',
                    (post_title, body, session['username']))
        sqlite3.connect.commit()

        cur.close()
        flash('Post created', 'success')
        return render_template('dashboard.html')
    return render_template('add_post.html', form=form)


@app.route('/edit_post/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_post(id):
    cur = sqlite3.connect.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", [id])
    post = cur.fetchone()
    form = PostForm(request.form)
    form.title.data = post['title']
    form.body.data = post['body']
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        cur = sqlite3.connect.cursor()
        cur.execute(
            'UPDATE posts SET title = %s, body = %s WHERE id = %s', (title, body, id))
        sqlite3.connect.commit()
        cur.close()
        flash('Post updated', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_post.html', form=form)


@app.route('/delete_post/<string:id>', methods=['POST'])
@is_logged_in
def delete_post(id):
    cur = sqlite3.connect.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s;", [id])
    sqlite3.connect.commit()
    cur.close()
    flash('Post Deleted', 'success')
    return redirect(url_for('dashboard'))


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
