from dataclasses import dataclass
import json
from flask import Flask, flash
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
        userId_input = request.form.get("userId", None)
        
        try:
            lock.acquire(True)
            user = cur.execute("SELECT * FROM users WHERE name=?", (username,)).fetchone()
        finally:
            lock.release()
        
        if user is not None:
            dbUsername = user[1]
            dbPassword = user[2]
            userId = user[0]
            if username == dbUsername and int(password) == int(dbPassword) and str(userId) == userId_input:
                if str(userId).startswith('3'):
                    session['user_id'] = userId
                    return redirect(url_for('studentHomePage'))
                elif str(userId).startswith('1'):
                    session['user_id'] = userId
                    return redirect(url_for('adminHomePage'))
                elif str(userId).startswith('2'):
                    session['user_id'] = userId
                    return redirect(url_for('teacherHomePage'))
    
    return render_template("login.html")



# signup
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    global id
    if request.method == 'POST':
        id += 1
        # sign up
        session.pop('user_id', None)  # clean before signup
        
        role = request.form.get("roles", None)
        firstName = request.form.get("new-userFirstName", None)
        lastName = request.form.get("new-userLastName", None)
        password = request.form.get("password", None)
        
        if role == "administrator":
            roleNum = 1
        elif role == "instructor":
            roleNum = 2
        else:
            roleNum = 3
        
        userId = roleNum * 1000 + id
        userName = firstName + " " + lastName
        data = (userId, userName, password, "")
        
        try:
            lock.acquire(True)
            user = cur.execute("INSERT INTO users VALUES(?,?,?,?)", data)  # insert user into db
            con.commit()
        finally:
            lock.release()
        
        return render_template("signup_success.html", userId=userId)  # Show success page with user ID
        
    return render_template("signup.html")




# studentHomePage
@app.route("/studentHomePage",methods=['GET', 'POST'])
def studentHomePage():
    user=cur.execute("SELECT * FROM users WHERE id=%d"%session['user_id']).fetchone()
    courses=user[3].split()
    print(courses)
    return render_template("studentHomePage.html", courses = courses)


@app.route("/coursePage_student", methods=['GET', 'POST'])
def coursePage_student():
    selectedCourse=request.args.get('type')
    session['selectedCourse']=selectedCourse


    # 查询数据库以获取与selectedCourse匹配的条目
    conn = sqlite3.connect("tutorial.db")
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT QuizName FROM quiz WHERE Course=?", (selectedCourse,))
    quiz_rows = cur.fetchall() 
    conn.close()
    # 创建一个quizList，仅包含唯一的QuizName
    quizList = [row[0] for row in quiz_rows]

    assignmentList = os.listdir('C:/Users/Haozhe XU/Desktop/COSC310/server/%s'%selectedCourse)
    return render_template('coursePage_student.html',
     assignmentList=assignmentList, quizList=quizList)




@app.route("/download/<path:filename>")
def download_file(filename):
    selectedCourse = session.get('selectedCourse')
    selectedAssignment=session['selectedAssignment']

    assignment_path = os.path.join('C:/Users/Haozhe XU/Desktop/COSC310/server', selectedCourse, selectedAssignment)
    return send_from_directory(assignment_path, filename, as_attachment=True)

@app.route("/assignmentPage_student", methods=['GET', 'POST'])
def assignmentPage_student():
    selectedCourse = session.get('selectedCourse')
    selectedAssignment=request.args.get('type')
    session['selectedAssignment']=selectedAssignment
    assignment_path = os.path.join('C:/Users/Haozhe XU/Desktop/COSC310/server', selectedCourse, selectedAssignment)

    if not os.path.exists(assignment_path):
        return "Error: Assignment folder does not exist"

    # 遍历指定路径下的所有文件
    file_list = [file_name for file_name in os.listdir(assignment_path) if file_name.startswith('2')]
    
    # 查询成绩信息
    grade = None
    
    searchData = (selectedCourse, selectedAssignment, str(session['user_id']))
    print(session['user_id'])
    gradeData = cur.execute("SELECT grade FROM grades WHERE courseName=? AND assignment=? AND studentId=?", searchData).fetchone()
    print(gradeData)
    if gradeData:
        grade = gradeData[0]

    return render_template('assignmentPage_student.html', file_list=file_list, grade=grade)



@app.route('/uploadAssignment', methods=['GET', 'POST'])
def uploadAssignment():
    selectedCourse = session.get('selectedCourse')
    selectedAssignment = session.get('selectedAssignment')

    if request.method == 'POST':
        # 检查是否存在文件在请求中
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        # 如果用户没有选择文件，浏览器也会发送一个空的文件名
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file:
            # 创建保存文件的文件夹路径
            assignment_path = os.path.join(app.config['UPLOAD_FOLDER'], selectedCourse, selectedAssignment)
            os.makedirs(assignment_path, exist_ok=True)

            # 保存文件到指定目录
            file_extension = file.filename.rsplit('.', 1)[-1]
            new_filename = f"{session['user_id']}.{file_extension}"
            file.save(os.path.join(assignment_path, new_filename))
            
            flash('File uploaded successfully', 'success')
            return redirect(request.url)

    return render_template('uploadAssignment.html')



# answer the quiz
from flask import request, render_template, session

@app.route('/quizPage_student', methods=['GET', 'POST'])
def quizPage_student():
    submitted = False  # 默认情况下，submitted为False

    selectedCourse = session.get('selectedCourse')
    
    user_id = session.get('user_id')

    if request.method == 'GET':
        selectedQuiz = request.args.get('type')
        session['selectedQuiz'] = selectedQuiz
    selectedQuiz = session.get('selectedQuiz')

    print(session)

    if selectedCourse is None or selectedQuiz is None:
        return "Error: No selected course or quiz"

    # 获取当前最高分数
    conn = sqlite3.connect('tutorial.db')
    cur = conn.cursor()
    cur.execute("SELECT grade FROM grades WHERE courseName=? AND assignment=? AND studentId=?", (selectedCourse, selectedQuiz, user_id))
    highest_score = cur.fetchone()
    conn.close()

    if highest_score:
        highest_score = highest_score[0]

    if request.method == 'POST':
        student_answers = {}
        correct_answers = {}
        result = {}

        # 获取学生的答案
        for key, value in request.form.items():
            if key.startswith('question_'):
                quiz_number = int(key.split('_')[-1])
                student_answers[quiz_number] = value

        # 连接数据库并获取正确答案
        conn = sqlite3.connect('tutorial.db')
        cur = conn.cursor()
        cur.execute("SELECT QuizNumber, Answer FROM quiz WHERE Course=? AND QuizName=?", (selectedCourse, selectedQuiz))
        rows = cur.fetchall()
        for row in rows:
            quiz_number, answer = row
            correct_answers[quiz_number] = answer
        conn.close()

        # 将学生答案与正确答案进行比较
        correct_count = 0
        for quiz_number, answer in student_answers.items():
            if answer == correct_answers.get(quiz_number):
                result[quiz_number] = "Correct"
                correct_count += 1
            else:
                result[quiz_number] = "Incorrect"

        submitted = True  # 设置submitted为True，表示已提交

        # 计算得分
        grade = f"{correct_count}/{len(correct_answers)}"

        # 连接数据库并存储成绩
        conn = sqlite3.connect('tutorial.db')
        cur = conn.cursor()

        # 如果数据库中已存在相同记录，则先删除
        cur.execute("DELETE FROM grades WHERE courseName=? AND assignment=? AND studentId=?", (selectedCourse, selectedQuiz, user_id))

        # 插入新的成绩记录
        cur.execute("INSERT INTO grades (courseName, assignment, studentId, grade) VALUES (?, ?, ?, ?)", (selectedCourse, selectedQuiz, user_id, grade))
        conn.commit()
        conn.close()

        return render_template('quizPage_student.html', result=result, correct_count=correct_count, total_questions=len(correct_answers), submitted=submitted, highest_score=highest_score)

    else:
        conn = sqlite3.connect('tutorial.db')
        cur = conn.cursor()

        # 获取与选定课程和测验名称匹配的条目
        cur.execute("SELECT * FROM quiz WHERE Course=? AND QuizName=?", (selectedCourse, selectedQuiz))
        quiz_questions = cur.fetchall()

        conn.close()

        return render_template('quizPage_student.html', quiz_questions=quiz_questions, submitted=submitted, highest_score=highest_score)







# teacherHomePage
@app.route("/teacherHomePage",methods=['GET', 'POST'])
def teacherHomePage():
    user=cur.execute("SELECT * FROM users WHERE id=%d"%session['user_id']).fetchone()
    courses=user[3].split()
    return render_template("teacherHomePage.html", courses = courses)

# coursePage_teacher
# 教师在课程页面上传作业，最后要把储存到数据库中的assignmentName改成“教师id+assignment”， courses改成对应课程
@app.route("/coursePage_teacher", methods=['GET', 'POST'])
def coursePage_teacher():
    selectedCourse=request.args.get('type')
    session['selectedCourse']=selectedCourse
    # 查询数据库以获取与selectedCourse匹配的条目
    conn = sqlite3.connect("tutorial.db")
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT QuizName FROM quiz WHERE Course=?", (selectedCourse,))
    quiz_rows = cur.fetchall()
    

    # 创建一个quizList，仅包含唯一的QuizName
    quizList = [row[0] for row in quiz_rows]
    print(quizList)

    assignmentList = cur.execute("SELECT * FROM assignment WHERE courseName=?",(selectedCourse,)).fetchall()

    conn.close()

    success_message = None
    if 'success' in session:
        success_message = session.pop('success')
        
    return render_template('coursePage_teacher.html', assignmentList=assignmentList, quizList=quizList,  success_message=success_message)

   

@app.route('/addAssignment', methods=['GET', 'POST'])
def add_assignment_page():
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        assignment_name = request.form.get('assignment_name')
        assignment_full_mark = request.form.get('assignmentFullMark')
    
        if file.filename == '':
            return 'No selected file'
        
        if file and assignment_name:
            try:
                selected_course = session['selectedCourse']
                # Check if assignment with same name exists in the database
                con = sqlite3.connect("tutorial.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM assignment WHERE assignmentName = ? AND courseName = ?", (assignment_name, selected_course))
                existing_assignment = cur.fetchone()
                
                if existing_assignment:
                    flash('Assignment already exists for this course!', 'error')
                    return render_template('addAssignment.html')
                
                # Create directory for assignment if it doesn't exist
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], selected_course, assignment_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                # Save file to the directory with user_id as filename
                file_extension = file.filename.rsplit('.', 1)[-1]
                new_filename = f"{session['user_id']}.{file_extension}"
                file.save(os.path.join(folder_path, new_filename))
                
                # Save assignment details to database
                cur.execute("INSERT INTO assignment (assignmentName, courseName, assignmentFullMark) VALUES (?, ?, ?)", (assignment_name, selected_course, assignment_full_mark))              
                con.commit()
                con.close()

                flash('Assignment created successfully!', 'success')  # Flash success message
                return redirect(url_for('coursePage_teacher', type=selected_course))
            except Exception as e:
                return f'An error occurred: {str(e)}'
        else:
            return 'Assignment name is required'
    else:
        return render_template('addAssignment.html')




@app.route('/createQuiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        quiz_name = request.form['quizName']
        course = session.get('selectedCourse', None)

        conn = sqlite3.connect('tutorial.db')
        cur = conn.cursor()

        try:
            selected_course = session['selectedCourse']
            # 检查是否已经存在同名测验
            cur.execute("SELECT QuizName FROM quiz WHERE QuizName=? AND Course=?", (quiz_name, course))
            existing_quiz = cur.fetchone()
            if existing_quiz:
                flash('A quiz with the same name already exists. Please choose a different name.', 'error')
                return redirect(url_for('create_quiz'))

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

            flash('Quiz created successfully!', 'success')  # Flash success message
            return redirect(url_for('coursePage_teacher', type=selected_course))

        # 处理异常情况
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error: {e}")

    return render_template('createQuiz.html')



@app.route("/assignmentPage_teacher", methods=['GET', 'POST'])
def assignmentPage_teacher():
    selectedAssignment = request.args.get('type')
    assignmentName = selectedAssignment
    selectedCourse = session['selectedCourse']
    session['selectedAssignment'] = selectedAssignment
    folder_path = os.path.join("C:/Users/Haozhe XU/Desktop/COSC310/server", selectedCourse, selectedAssignment)
    
    # 仅遍历以3开头的文件
    submissionList = [file_name for file_name in os.listdir(folder_path) if file_name.startswith('3')]
    length = len(submissionList)
    gradeList = []

    for i in range(length):
        stuId=submissionList[i].split(".")[0]
        print(selectedCourse)
        print(selectedAssignment)
        print(int(stuId))
        data = (selectedCourse,selectedAssignment,int(stuId))
        grades = cur.execute("SELECT * FROM grades WHERE courseName=? AND assignment=? AND studentId=?",data).fetchone()
        print(grades)
        if grades is None:
            gradeList.append("Not Graded Yet")
        else:
            gradeList.append(grades[3])
    print(submissionList)
    
    return render_template('assignmentPage_teacher.html', submissionList=submissionList, assignmentName=assignmentName, length=length, gradeList=gradeList)



@app.route("/quizPage_teacher", methods=['GET', 'POST'])
def quizPage_teacher():
    selected_quiz = request.args.get('type')
    quiz_name = selected_quiz
    selected_course = session.get('selectedCourse')
    session['selectedQuiz'] = selected_quiz

    conn = sqlite3.connect("tutorial.db")
    cur = conn.cursor()

    # 查询成绩表中符合条件的记录
    cur.execute("SELECT studentId, grade FROM grades WHERE courseName=? AND assignment=?", (selected_course, selected_quiz))
    grade_records = cur.fetchall()

    # 提取学生ID和成绩
    grade_info = [{'studentId': record[0], 'grade': record[1]} for record in grade_records]

    conn.close()

    return render_template('quizPage_teacher.html', quizName=quiz_name, gradeInfo=grade_info)











@app.route("/courses", methods=['GET', 'POST'])
def courses():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return "User not logged in"

    # 获取用户ID
    user_id = session['user_id']

    # 获取用户已选课程列表
    user_courses = cur.execute("SELECT courses FROM users WHERE id = ?", (user_id,)).fetchone()
    if user_courses:
        user_courses = user_courses[0]
    else:
        return "User not found"

    # 获取所有课程列表
    courseList = cur.execute("SELECT * FROM courses").fetchall()

    if request.method == 'POST':
        student_input = request.form.get("student_input", None)
        if student_input:
            # 检查用户输入的课程是否已经在用户已选课程列表中
            if student_input in user_courses:
                return render_template('courses.html', status="course already selected", courseList=courseList)
            
            # 检查用户是否已经发送过申请
            existing_applications = cur.execute("SELECT courseName FROM application WHERE studentId = ?", (user_id,)).fetchall()
            if existing_applications:
                for app_course in existing_applications:
                    if app_course[0] == student_input:
                        return render_template('courses.html', status="application already sent", courseList=courseList)
            
            # 检查用户输入的课程是否存在于课程表中
            course_exists = cur.execute("SELECT * FROM courses WHERE courseName = ?", (student_input,)).fetchone()
            if not course_exists:
                return render_template('courses.html', status="course does not exist", courseList=courseList)

            # 发送申请
            try:
                lock.acquire(True)
                cur.execute("INSERT INTO application (studentId, courseName) VALUES (?, ?)", (user_id, student_input))
                con.commit()
            finally:
                lock.release()
                
            return render_template('courses.html', status="sent application", courseList=courseList)

    return render_template('courses.html', courseList=courseList)








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
        


@app.route("/createCoursePage", methods=['GET', 'POST'])
def createCoursePage():
    if request.method == 'POST':
        courseName = request.form.get("courseName", None)
        instructor = request.form.get("instructor", None)
        data = (courseName, instructor)
        try:
            con = sqlite3.connect("tutorial.db")
            cur = con.cursor()
            
            # Check if course already exists
            cur.execute("SELECT * FROM courses WHERE courseName=?", (courseName,))
            existing_course = cur.fetchone()
            if existing_course:
                flash("Course already exists!", "error")
            else:
                cur.execute("INSERT INTO courses (courseName, instructor) VALUES (?, ?)", data)

                teacherData = cur.execute("SELECT * FROM users WHERE name=?", (instructor,)).fetchone()
                teacherCourses = teacherData[3]
                teacherCourses = teacherCourses + " " + courseName
                newData = (teacherData[0], teacherData[1], teacherData[2], teacherCourses)
                nameData = (instructor,)
                # update user table 
                cur.execute("DELETE FROM users WHERE name=?", nameData)
                cur.execute("INSERT INTO users VALUES(?,?,?,?)", newData)
                
                con.commit()
                # calling add course folder function
                create_course_folder(courseName)
                
                flash("Course created successfully!", "success")
                return render_template("adminHomePage.html")
        except sqlite3.Error as e:
            print("Error inserting course:", e)
        finally:
            con.close()
    
    # Fetch instructors whose usernames start with '2'
    users = get_instructors()

    return render_template("createCoursePage.html", users=users)

def get_instructors():
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

    return users





@app.route("/AdminRequests",methods=['GET','POST'])
def AdminRequests():
    applicationList = []
    length = 0
    applicationList=cur.execute("SELECT * FROM application").fetchall()
    if len(applicationList)==0:
        return render_template('AdminRequests.html',applicationList=applicationList,length=length)
    length=len(applicationList)
    # get all applications
    try:
        lock.acquire(True)
        # for i in range(length):
        approved=request.form.get("numberApproved")
        print(approved)
        if approved is not None:
            approved=int(approved)
            print(approved)
        else:
            return render_template('AdminRequests.html',applicationList=applicationList,length=length)
        studentId=applicationList[approved][0]
        courseName=applicationList[approved][1]
        data=(studentId,courseName)
        # delete approved application
        cur.execute("DELETE FROM application WHERE studentId=? AND courseName=?",data)
        studentData=cur.execute("SELECT * FROM users WHERE id=%d" % studentId).fetchone()
        stuCourses=studentData[3]
        stuCourses=stuCourses+" "+courseName
        newData=(studentData[0],studentData[1],studentData[2],stuCourses)
        idData=(studentId,)
        # update user table 
        cur.execute("DELETE FROM users WHERE id=?",idData)
        cur.execute("INSERT INTO users VALUES(?,?,?,?)",newData)
        con.commit()
    finally:
        lock.release()
    return render_template('AdminRequests.html',applicationList=applicationList,length=length)





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
    data=(session['selectedCourse'],session['selectedAssignment'],selectedStudent)
    grade=cur.execute("SELECT grade FROM grades WHERE courseName=? AND assignment=? AND studentId=?",data)
    try:
        lock.acquire(True)
        cur.execute("INSERT INTO grades VALUES(?,?,?,?)",data)
        con.commit()
    finally:
        lock.release()
    return render_template('grading.html')




@app.route("/TeacherGrade", methods=['GET', 'POST'])
def TeacherGrade():
    selectedStudent = request.args.get('type').split(".")[0]
    session['selectedStudent'] = selectedStudent
    newGrade = request.form.get("grade", None)
    
    courseName = session['selectedCourse']
    assignmentName = session['selectedAssignment']
    studentId = session['selectedStudent']
    studentId = int(studentId)
    studentName = cur.execute("SELECT * FROM users WHERE id=%d" % studentId).fetchone()[1]

    if request.method == 'POST':
        try:
            # 删除原始记录
            searchData = (courseName, assignmentName, studentId)
            cur.execute("DELETE FROM grades WHERE courseName=? AND assignment=? AND studentId=?", searchData)
            # 插入新记录
            data = (courseName, assignmentName, studentId, newGrade)
            lock.acquire(True)
            cur.execute("INSERT INTO grades VALUES (?, ?, ?, ?)", data)
            con.commit()
            flash('Grade submitted successfully!', 'success')
        except Exception as e:
            con.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            lock.release()
        return render_template('TeacherGrade.html', courseName=courseName, assignmentName=assignmentName, studentName=studentName, studentId=studentId)

    return render_template('TeacherGrade.html', courseName=courseName, assignmentName=assignmentName, studentName=studentName, studentId=studentId)





@app.route("/discussions",methods=['GET','POST'])
def discussions():
    discussions = cur.execute("SELECT DISTINCT discussionName FROM discussions").fetchall()
    discussionList=list()
    for d in discussions:
        discussionList.append(d[0])

    return render_template('discussions.html',discussionList=discussionList)

@app.route("/newDiscussion",methods=['GET','POST'])
def newDiscussion():
    if request.method == 'POST':
        discussionName=request.form.get("discussionName",None)
        discussionContent=request.form.get("discussionContent",None)
        data = (discussionName,discussionContent,'')
        try:
            lock.acquire(True)
            cur.execute("INSERT INTO discussions VALUES(?,?,?)",data)
            con.commit()
        finally:
            lock.release()
        return redirect(url_for('discussions'))
    return render_template('newDiscussion.html')


@app.route("/oneDiscussion",methods=['GET','POST'])
def oneDiscussion():
    selectedDiscussion = request.args.get('type')
    session['selectedDiscussion']=selectedDiscussion
    print(selectedDiscussion)
    discussionData = cur.execute("SELECT * FROM discussions WHERE discussionName=?",(selectedDiscussion,)).fetchall()
    content=discussionData[0][1]
    replyList=list()
    for d in discussionData:
        if d[2] != '':
            replyList.append(d[2])
    if request.method == 'POST':
        userInput = request.form.get("reply",None)
        userName=cur.execute("SELECT * FROM users WHERE id=%d"%g.user[0]).fetchone()[1]
        userInput=userName+": "+userInput
        data=(selectedDiscussion,content,userInput)
        try:
            lock.acquire(True)
            cur.execute("INSERT INTO discussions VALUES(?,?,?)",data)
            con.commit()
        finally:
            lock.release()
        return render_template('oneDiscussion.html',discussionName=selectedDiscussion,content=content,replyList=replyList)
    return render_template('oneDiscussion.html',discussionName=selectedDiscussion,content=content,replyList=replyList)