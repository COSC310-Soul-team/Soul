from dataclasses import dataclass
from flask import Flask
from flask import request, render_template, redirect, url_for, session, g
import sqlite3
import threading

import os
import time

from flask import Flask, render_template, request, send_from_directory


con = sqlite3.connect("tutorial.db",check_same_thread=False)
cur = con.cursor()
id=0
lock = threading.Lock()
# cur.execute("CREATE TABLE users(id, name, password)")
# res=cur.execute("INSERT INTO users VALUES (2,'xu',333)")
# con.commit()


app = Flask(__name__, static_url_path="/")
app.config['SECRET_KEY'] = "sdfklas0lk42j"




@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        try:
            lock.acquire(True)
            user = cur.execute("SELECT * FROM users WHERE id=%d" % session['user_id']).fetchone() #find user in database
            g.user = user #this is a tuple now
        finally:
            lock.release()


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    
        session.pop('user_id', None) 
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        try:
            lock.acquire(True)
            user = cur.execute("SELECT * FROM users WHERE name='%s'"%username).fetchone() 
        finally:
            lock.release()
        if not user==None: 
            dbPassword = user[2]
            userId = user[0]
            password = password
            if password == dbPassword: 
                if str(userId).startswith('3'):
                    session['user_id'] = userId
                    return redirect(url_for('courses'))
                elif str(userId).startswith('1'):
                    session['user_id'] = userId
                    return redirect(url_for('adminHomePage'))
                elif str(userId).startswith('2'):
                    session['user_id'] = userId
                    return redirect(url_for('teacherHomePage'))

    return render_template("login.html")


# studentHomePage
@app.route("/studentHomePage")
def studentHomePage():
    return render_template("studentHomePage.html")

# teacherHomePage
@app.route("/teacherHomePage")
def teacherHomePage():
    return render_template("teacherHomePage.html")

# adminHomePage
@app.route("/adminHomePage")
def adminHomePage():
    return render_template("adminHomePage.html")





# signup
@app.route("/signup",methods=['GET', 'POST'])
def signup():
    global id
    if request.method == 'POST':
        id+=1
        print("post")
        # sign up
        session.pop('user_id', None) #clean before signup
        
        role = request.form.get("roles",None)
        firstName = request.form.get("new-userFirstName", None)
        lastName = request.form.get("new-userLastName", None)
        # username = request.form.get("username", None)
        password = request.form.get("password", None)
        if role == "Administrator":
            roleNum=1
        elif role == "Instructor":
            roleNum=2
        else:
            roleNum=3
        userId=roleNum*1000+id
        userName=firstName+" "+lastName
        # role = 1/2/3?
        print(role)
        data=(userId,userName,password)
        print(data)
        try:
            lock.acquire(True)
            user = cur.execute("INSERT INTO users VALUES(?,?,?)",data) #insert user into db
            con.commit()
        finally:
            lock.release()
        return redirect(url_for('login'))
    return render_template("signup.html")





@app.route("/courses",methods=['GET','POST'])
def courses():
    # g.user=
    courseList=cur.execute("SELECT * FROM courses").fetchall()
    # courseList='\n'.join(courseList)
    # courseList=list(courseList.split(" "))
    # print(courseList[0])
    courseNames=cur.execute("SELECT courseName FROM courses").fetchall()
    studentInput=request.form.get("student_input",None)
    print(studentInput)
    for name in courseNames:
        print(name[0])
        if name[0]==studentInput:
            data=(g.user[0],1,name[0])            
            try:
                lock.acquire(True)
                cur.execute("INSERT INTO application VALUES(?,?)",data)
                con.commit()
            finally:
                lock.release()
            return render_template('courses.html',status="sent application",courseList=courseList)
    return render_template('courses.html',courseList=courseList)







# upload file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    return render_template('upload.html')

app.config['UPLOAD_FOLDER'] = r'C:\Users\Haozhe XU\Desktop\COSC310\server'
file_dir = app.config['UPLOAD_FOLDER']

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    """
        upload file
    """
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        print(request.files, f.filename)

        return 'upload successfully!'
    else:
        return render_template('upload.html')
    






# download file
@app.route('/download', methods=['GET', 'POST'])
def download():
    """
        download file
    :return:
    """
    timelist = []   
    Foder_Name = []     
    Files_Name = []  

    lists = os.listdir(r'C:\Users\Haozhe XU\Desktop\COSC310\server')

    for i in lists:
        timelist.append(time.ctime(os.path.getatime(r'C:\Users\Haozhe XU\Desktop\COSC310\server' + '\\' + i)))

    for k in range(len(lists)):
        Files_Name.append(lists[k])

    print(r'C:\Users\Haozhe XU\Desktop\COSC310\server') 

    return render_template('download.html', allname=Foder_Name, name=Files_Name)

@app.route('/downloads/<path:path>', methods=['GET', 'POST'])
def downloads(path):
    """
        download file
    :param path:
    :return:
    """ 
    return send_from_directory(r'C:\Users\Haozhe XU\Desktop\COSC310\server', path, as_attachment=True)