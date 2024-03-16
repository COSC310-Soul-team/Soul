from dataclasses import dataclass
from flask import Flask
from flask import request, render_template, redirect, url_for, session, g
import sqlite3
import threading
con = sqlite3.connect("tutorial.db",check_same_thread=False)
cur = con.cursor()
id=0
lock = threading.Lock()

# cur.execute("CREATE TABLE users(id, name, password)")
# res=cur.execute("INSERT INTO users VALUES (2,'xu',333)")
# con.commit()



app = Flask(__name__, static_url_path="/")
app.config['SECRET_KEY'] = "sdfklas0lk42j"


@dataclass
class User:
    id: int
    username: str
    password: str

users = [
	User(1, "Admin", "123456"),
	User(2, "Eason", "888888"),
	User(3, "Tommy", "666666"),
]

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        try:
            lock.acquire(True)
            user = cur.execute("SELECT * FROM users WHERE id=%d" % session['user_id']).fetchone() #find user in database
            g.user = user#this is a tuple now
        finally:
            lock.release()

# login界面
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 登录操作
        session.pop('user_id', None) #登陆前清空
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        try:
            lock.acquire(True)
            user = cur.execute("SELECT * FROM users WHERE name='%s'"%username).fetchone() #比对前台输入和后台数据库
        finally:
            lock.release()
        if not user==None: #返回的非空数据（有用户）
            dbPassword = user[2]
            userId = user[0]
            password=int(password)
            dbPassword=int(dbPassword)
            if password == dbPassword:#password in db
                session['user_id'] = userId #valid user, save userid to session
                return redirect(url_for('profile')) #redirect to profile

    return render_template("login.html")

#logged in, profile page
@app.route("/profile")
def profile():
    #判断是否有该用户，没有则跳转回login界面
    if not g.user:
        return redirect(url_for('login'))
    
    return render_template("profile.html")


#signup page
@app.route("/signup")
def signup():
    if request.method == 'POST':
        # sign up
        session.pop('user_id', None) #clean before signup
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        # role = 1/2/3?
        data=[(id,username,password)]
        try:
            lock.acquire(True)
            user = cur.execute("INSERT INTO users VALUES(?, ?, ?)", data) #insert user into db
        finally:
            lock.release()
    print("sign up")
    return render_template("signup.html")