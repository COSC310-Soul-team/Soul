from dataclasses import dataclass
import json
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

#文件路径
app.config['UPLOAD_FOLDER'] = r'C:\Users\Haozhe XU\Desktop\COSC310\server'
file_dir = app.config['UPLOAD_FOLDER']



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
@app.route("/studentHomePage",methods=['GET', 'POST'])
def studentHomePage():
    return render_template("studentHomePage.html")


# answer the quiz
@app.route('/quizPage_student', methods=['GET', 'POST'])
def quiz_page_student():
    submitted = False  # 默认情况下，submitted为False
    if request.method == 'POST':
        student_answers = {}
        correct_answers = {}
        result = {}

        # Get student's answers
        for key, value in request.form.items():
            if key.startswith('question_'):
                quiz_number = int(key.split('_')[-1])
                student_answers[quiz_number] = value

        # Connect to the database and get correct answers
        conn = sqlite3.connect('tutorial.db')
        cur = conn.cursor()
        cur.execute("SELECT QuizNumber, Answer FROM quiz")
        rows = cur.fetchall()
        for row in rows:
            quiz_number, answer = row
            correct_answers[quiz_number] = answer
        conn.close()

        # Compare student answers with correct answers
        correct_count = 0
        for quiz_number, answer in student_answers.items():
            if answer == correct_answers.get(quiz_number):
                result[quiz_number] = "Correct"
                correct_count += 1
            else:
                result[quiz_number] = "Incorrect"

        submitted = True  # 设置submitted为True，表示已提交
        #在前端会刷新这个页面，从而使submit和选项不再显示

        return render_template('quizPage_student.html', result=result, correct_count=correct_count, total_questions=len(correct_answers), submitted=submitted)

    else:
        conn = sqlite3.connect('tutorial.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM quiz")
        quiz_questions = cur.fetchall()

        conn.close()

        return render_template('quizPage_student.html', quiz_questions=quiz_questions, submitted=submitted)






# teacherHomePage
@app.route("/teacherHomePage",methods=['GET', 'POST'])
def teacherHomePage():
    return render_template("teacherHomePage.html")

# coursePage_teacher
# 教师在课程页面上传作业，最后要把储存到数据库中的assignmentName改成“教师id+assignment”， courses改成对应课程
@app.route("/coursePage_teacher", methods=['GET', 'POST'])
def coursePage_teacher():
    if request.method == 'POST':
        assignment_name = request.form.get("assignment_name", None)
        file = request.files.get("file")
        if file and assignment_name:
            try:
                # Create a directory with assignment_name if it doesn't exist
                folder_path = os.path.join("C:/Users/Haozhe XU/Desktop/COSC310/server", assignment_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                # Save file to the directory
                file.save(os.path.join(folder_path, file.filename))
                
                # Save assignment details to database
                con = sqlite3.connect("tutorial.db")
                cur = con.cursor()
                cur.execute("INSERT INTO assignment (assignmentName, courseName) VALUES (?, ?)", (assignment_name, os.path.join("your_upload_directory/", assignment_name, file.filename)))
                con.commit()
                con.close()
                
            except sqlite3.Error as e:
                print("Error inserting assignment:", e)
        
        return redirect(url_for('coursePage_teacher'))
    
    timelist = []   
    Folder_Name = []     
    Files_Name = []  

    lists = os.listdir(r'C:\Users\Haozhe XU\Desktop\COSC310\server')

    for i in lists:
        timelist.append(time.ctime(os.path.getatime(r'C:\Users\Haozhe XU\Desktop\COSC310\server' + '\\' + i)))

    for k in range(len(lists)):
        Files_Name.append(lists[k])

    print(r'C:\Users\Haozhe XU\Desktop\COSC310\server') 
    
    return render_template("coursePage_teacher.html", allname=Folder_Name, name=Files_Name)

@app.route('/coursePage_teacher/<path:path>', methods=['GET', 'POST'])
def downloads(path):
    """
        download file
    :param path:
    :return:
    """ 
    return send_from_directory(r'C:\Users\Haozhe XU\Desktop\COSC310\server', path, as_attachment=True)



@app.route('/createQuiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quizName']
        course = request.form.get('course', None)  # 目前没有链接课程，所以课程设置为NULL

        conn = sqlite3.connect('tutorial.db')
        cur = conn.cursor()

        try:
            # 遍历表单中的每道题目
            for key, value in request.form.items():
                # 如果字段名称以 "question_" 开头，说明是题目相关字段
                if key.startswith('question_'):
                    question_number = key.split('_')[-1]
                    question = request.form[f'question_{question_number}']
                    option_a = request.form[f'optionA_{question_number}']
                    option_b = request.form[f'optionB_{question_number}']
                    option_c = request.form[f'optionC_{question_number}']
                    option_d = request.form[f'optionD_{question_number}']
                    answer = request.form[f'answer_{question_number}']

                    # 插入题目数据
                    cur.execute('''INSERT INTO quiz (QuizName, Course, QuizNumber, Question, OptionA, OptionB, OptionC, OptionD, Answer) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (quiz_name, course, question_number, question, option_a, option_b, option_c, option_d, answer))

            # 提交事务并关闭连接
            conn.commit()
            conn.close()

            return redirect(url_for('create_quiz'))

        #solve the exceptions
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error: {e}")

    return render_template('createQuiz.html')










# upload file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    return render_template('upload.html')
# upload file
#更改路径至'C:\Users\Haozhe XU\Desktop\COSC310\server\课程名'

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    """
        upload file
    """
    if request.method == 'POST':
        f = request.files['file']
        
        #更改文件名，最后替换成对应页面的id
        f.filename = '123' + os.path.splitext(f.filename)[1]

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        print(request.files, f.filename)

        return redirect(request.referrer)
    else:
        return redirect(request.referrer)
    
    





# adminHomePage
@app.route("/adminHomePage",methods=['GET', 'POST'])
def adminHomePage():
    return render_template("adminHomePage.html")

# create courses
# create course folder function
def create_course_folder(course_name):
    folder_path = os.path.join("C:\\Users\\Haozhe XU\\Desktop\\COSC310\\server", course_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        print("Folder already exists")
# createCoursePage
@app.route("/createCoursePage", methods=['GET', 'POST'])
def createCoursePage():
    if request.method == 'POST':
        courseName = request.form.get("courseName", None)
        instructor = request.form.get("instructor", None)
        data = (courseName, instructor)
        try:
            con = sqlite3.connect("tutorial.db")
            cur = con.cursor()
            cur.execute("INSERT INTO courses (courseName, instructor) VALUES (?, ?)", data)
            con.commit()
            # calling add course folder function
            create_course_folder(courseName)
        except sqlite3.Error as e:
            print("Error inserting course:", e)
        finally:
            con.close()
        return redirect(url_for('adminHomePage'))
    
    # Fetch instructors whose usernames start with '2'
    users = []
    try:
        con = sqlite3.connect("tutorial.db")
        cur = con.cursor()
        cur.execute("SELECT name FROM users WHERE id LIKE '2%'")
        rows = cur.fetchall()
        users = [row[0] for row in rows]
    except sqlite3.Error as e:
        print("Error fetching users:", e)
    finally:
        con.close()

    return render_template("createCoursePage.html", users=users)




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
        print(role)
        if role == "administrator":
            roleNum=1
        elif role == "instructor":
            roleNum=2
        else:
            roleNum=3
        userId=roleNum*1000+id
        userName=firstName+" "+lastName
        # role = 1/2/3?
        print(role)
        data=(userId,userName,password,"")
        print(data)
        try:
            lock.acquire(True)
            user = cur.execute("INSERT INTO users VALUES(?,?,?,?)",data) #insert user into db
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






















@app.route("/dashBoard",methods=['GET','POST'])
def dashBoard():

    user=cur.execute("SELECT * FROM users WHERE id=%d"%session['user_id']).fetchone()
    print(session['user_id'])
    print(user)
    courses=user[3].split()
    role=user[0]
    if role>3000:
        roleNum=3#student
    elif role>2000:
        roleNum=2#instructor
    else:
        roleNum=1#admin
    
    return render_template('dashBoard.html',courses=courses,roleNum=roleNum)

@app.route("/coursePage",methods=['GET','POST'])
def coursePage():
    selectedCourse=request.args.get('type')
    session['selectedCourse']=selectedCourse
    return render_template('coursePage.html')

@app.route("/assignmentPage",methods=['GET','POST'])
def assignmentPage():
    #select which assignment, e.g. A1, A2    
    course=session['selectedCourse']
    print(course)
    assignments=cur.execute("SELECT * FROM assignments WHERE courseName='%s'"%course).fetchall()
    print(assignments)
    assignmentList=list()
    for a in assignments:
        assignmentList.append(a[1])
    print(assignmentList)
    return render_template('assignmentPage.html',assignments=assignmentList)

@app.route("/assignment",methods=['GET','POST'])
def assignment():
    #select which student, e.g. 3001, 3002
    selectedAssignment=request.args.get('type')
    session['selectedAssignment']=selectedAssignment
    studentAssignments=[3001,3002,3003]
    return render_template('assignment.html',studentAssignments=studentAssignments)

@app.route("/grading",methods=['GET','POST'])
def grading():
    selectedStudent=request.args.get('type')
    session['selectedStudent']=selectedStudent
    
    #get instructor input
    data=(session['selectedCourse'],session['selectedAssignment'],selectedStudent,newGrade)
    grade=cur.execute("SELECT grade FROM grades WHERE courseName=? AND assignment=? AND studentId=?",data)
    try:
        lock.acquire(True)
        cur.execute("INSERT INTO grades VALUES(?,?,?,?)",data)
        con.commit()
    finally:
        lock.release()
    return render_template('grading.html')