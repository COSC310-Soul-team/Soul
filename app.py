from dataclasses import dataclass
from flask import Flask
from flask import request, render_template, redirect, url_for, session, g



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

#调取user信息
@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [u for u in users if u.id == session['user_id']][0]
        g.user = user

# login界面
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 登录操作
        session.pop('user_id', None) #登陆前清空
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        user = [u for u in users if u.username==username] #比对前台输入和后台数据库
        if len(user) > 0: #返回的非空数据（有用户）
            user = user[0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))

    return render_template("login.html")

#登陆成功，用户界面
@app.route("/profile")
def profile():
    return render_template("profile.html")





