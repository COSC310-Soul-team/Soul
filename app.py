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


app = Flask(__name__, static_url_path="/")
app.config['SECRET_KEY'] = "sdfklas0lk42j"

#file path
path1=r'C:\Users\Allen\OneDrive\桌面\Soul final\server'
paraPath='C:/Users/Allen/OneDrive/桌面/Soul final/server'
app.config['UPLOAD_FOLDER'] = path1
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
        userId_input = int(request.form.get("userId", None))
        
        try:
            lock.acquire(True)
            user = cur.execute("SELECT * FROM users WHERE id=?", (userId_input,)).fetchone()
        finally:
            lock.release()
        
        if user is not None:
            dbUsername = user[1]
            dbPassword = int(user[2])
            userId = user[0]
            print(userId)
            print(dbPassword)
            print(dbUsername)
            if username == dbUsername and int(password) == int(dbPassword) and userId == userId_input:
                print(1)
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







@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        user_id = int(request.form['userId'])
        password = str(request.form['password'])
        new_user_name = request.form['newUserName']
        new_password = request.form['newPassword']

        # check if user exist
        cur.execute("SELECT * FROM users WHERE id=? AND password=?", (user_id, password))
        user = cur.fetchone()

        print(user)
        print(user_id)
        print(password)
        print(new_user_name)
        print(new_password)

        if user:
            # update user info
            cur.execute("UPDATE users SET name=?, password=? WHERE id=?", (new_user_name, new_password, user_id))
            con.commit()
            return redirect(url_for('login')) 
        else:
            # user not exist or wrong password
            return "User ID or Password is incorrect. Please try again."

    return render_template("profile.html")







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
        
        return render_template("signup_success.html", userId=userId, userName=userName)  # Show success page with user ID
        
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

    # get items with selectedCourse
    # conn = sqlite3.connect("tutorial.db")
    # cur = conn.cursor()
    cur.execute("SELECT DISTINCT QuizName FROM quiz WHERE Course=?", (selectedCourse,))
    quiz_rows = cur.fetchall() 
    # conn.close()
    # create a quizList，with unique QuizName
    quizList = [row[0] for row in quiz_rows]

    assignmentList = cur.execute("SELECT * FROM assignment WHERE courseName=?",(selectedCourse,))
    return render_template('coursePage_student.html',
     assignmentList=assignmentList, quizList=quizList)




@app.route("/download/<path:filename>")
def download_file(filename):
    selectedCourse = session.get('selectedCourse')
    selectedAssignment=session['selectedAssignment']

    assignment_path = os.path.join(paraPath, selectedCourse, selectedAssignment)
    return send_from_directory(assignment_path, filename, as_attachment=True)

@app.route("/assignmentPage_student", methods=['GET', 'POST'])
def assignmentPage_student():
    selectedCourse = session.get('selectedCourse')
    selectedAssignment=request.args.get('type')
    session['selectedAssignment']=selectedAssignment
    assignment_path = os.path.join(paraPath, selectedCourse, selectedAssignment)

    if not os.path.exists(assignment_path):
        return "Error: Assignment folder does not exist"

    # travers all files in the directory
    file_list = [file_name for file_name in os.listdir(assignment_path) if file_name.startswith('2')]
    
    # check grade
    grade = None
    
    searchData = (selectedCourse, selectedAssignment, session['user_id'])
    print(session['user_id'])
    gradeData = cur.execute("SELECT grade FROM grades WHERE courseName=? AND assignment=? AND studentId=?", searchData).fetchone()
    
    if gradeData:
        grade = gradeData[0]

    return render_template('assignmentPage_student.html', file_list=file_list, grade=grade)



@app.route('/uploadAssignment', methods=['GET', 'POST'])
def uploadAssignment():
    selectedCourse = session.get('selectedCourse')
    selectedAssignment = session.get('selectedAssignment')

    if request.method == 'POST':
        # check if file exist
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        # browser send null file name if user select no file
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file:
            # create save directory
            assignment_path = os.path.join(app.config['UPLOAD_FOLDER'], selectedCourse, selectedAssignment)
            os.makedirs(assignment_path, exist_ok=True)

            # save to specified directory
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
    submitted = False  # default submitted as False

    selectedCourse = session.get('selectedCourse')
    
    user_id = session.get('user_id')

    if request.method == 'GET':
        selectedQuiz = request.args.get('type')
        session['selectedQuiz'] = selectedQuiz
    selectedQuiz = session.get('selectedQuiz')

    print(session)

    if selectedCourse is None or selectedQuiz is None:
        return "Error: No selected course or quiz"

    # get grade
    conn = sqlite3.connect('tutorial.db')
    # cur = conn.cursor()
    cur.execute("SELECT grade FROM grades WHERE courseName=? AND assignment=? AND studentId=?", (selectedCourse, selectedQuiz, user_id))
    highest_score = cur.fetchone()
    # conn.close()

    if highest_score:
        highest_score = highest_score[0]

    if request.method == 'POST':
        student_answers = {}
        correct_answers = {}
        result = {}

        # get student ans
        for key, value in request.form.items():
            if key.startswith('question_'):
                quiz_number = int(key.split('_')[-1])
                student_answers[quiz_number] = value

        # get correct ans
        # conn = sqlite3.connect('tutorial.db')
        # cur = conn.cursor()
        cur.execute("SELECT QuizNumber, Answer FROM quiz WHERE Course=? AND QuizName=?", (selectedCourse, selectedQuiz))
        rows = cur.fetchall()
        for row in rows:
            quiz_number, answer = row
            correct_answers[quiz_number] = answer
        # conn.close()

        # compare student ans with correct ans
        correct_count = 0
        for quiz_number, answer in student_answers.items():
            if answer == correct_answers.get(quiz_number):
                result[quiz_number] = "Correct"
                correct_count += 1
            else:
                result[quiz_number] = "Incorrect"

        submitted = True  

        # calculate score
        grade = f"{correct_count}/{len(correct_answers)}"

        # store grafe
        # conn = sqlite3.connect('tutorial.db')
        # cur = conn.cursor()

        # if record exist, delete
        cur.execute("DELETE FROM grades WHERE courseName=? AND assignment=? AND studentId=?", (selectedCourse, selectedQuiz, user_id))

        # insert new grade
        cur.execute("INSERT INTO grades (courseName, assignment, studentId, grade) VALUES (?, ?, ?, ?)", (selectedCourse, selectedQuiz, user_id, grade))
        con.commit()
        # conn.close()

        return render_template('quizPage_student.html', result=result, correct_count=correct_count, total_questions=len(correct_answers), submitted=submitted, highest_score=highest_score)

    else:
        # conn = sqlite3.connect('tutorial.db')
        # cur = conn.cursor()

        cur.execute("SELECT * FROM quiz WHERE Course=? AND QuizName=?", (selectedCourse, selectedQuiz))
        quiz_questions = cur.fetchall()

        # conn.close()

        return render_template('quizPage_student.html', quiz_questions=quiz_questions, submitted=submitted, highest_score=highest_score)







# teacherHomePage
@app.route("/teacherHomePage",methods=['GET', 'POST'])
def teacherHomePage():
    user=cur.execute("SELECT * FROM users WHERE id=%d"%session['user_id']).fetchone()
    courses=user[3].split()
    return render_template("teacherHomePage.html", courses = courses)

# coursePage_teacher
# teacher upload assignment on course page，store assignment(assignmentName)as “teacherId+assignment”，change course to corresponding course
@app.route("/coursePage_teacher", methods=['GET', 'POST'])
def coursePage_teacher():
    selectedCourse=request.args.get('type')
    session['selectedCourse']=selectedCourse
    # get distinct quizes in selectedCourse
    # conn = sqlite3.connect("tutorial.db")
    # cur = conn.cursor()
    cur.execute("SELECT DISTINCT QuizName FROM quiz WHERE Course=?", (selectedCourse,))
    quiz_rows = cur.fetchall()
    

    # create quizList，with unique QuizName
    quizList = [row[0] for row in quiz_rows]
    print(quizList)

    assignmentList = cur.execute("SELECT * FROM assignment WHERE courseName=?",(selectedCourse,)).fetchall()

    # conn.close()

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
                # con.close()

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

        # conn = sqlite3.connect('tutorial.db')
        # cur = conn.cursor()

        try:
            selected_course = session['selectedCourse']
            # duplicate name check
            cur.execute("SELECT QuizName FROM quiz WHERE QuizName=? AND Course=?", (quiz_name, course))
            existing_quiz = cur.fetchone()
            if existing_quiz:
                flash('A quiz with the same name already exists. Please choose a different name.', 'error')
                return redirect(url_for('create_quiz'))

            # traverse all questions
            for key, value in request.form.items():
                # if start with "question_" it's the question
                if key.startswith('question_'):
                    question_number = key.split('_')[-1]
                    question = request.form[f'question_{question_number}']
                    option_a = request.form[f'optionA_{question_number}']
                    option_b = request.form[f'optionB_{question_number}']
                    option_c = request.form[f'optionC_{question_number}']
                    option_d = request.form[f'optionD_{question_number}']
                    answer = request.form[f'answer_{question_number}']

                    # insert quiz
                    cur.execute('''INSERT INTO quiz (QuizName, Course, QuizNumber, Question, OptionA, OptionB, OptionC, OptionD, Answer) 
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (quiz_name, course, question_number, question, option_a, option_b, option_c, option_d, answer))

            con.commit()
            # conn.close()

            flash('Quiz created successfully!', 'success')  # Flash success message
            return redirect(url_for('coursePage_teacher', type=selected_course))

        except Exception as e:
            # conn.rollback()
            # conn.close()
            print(f"Error: {e}")

    return render_template('createQuiz.html')



@app.route("/assignmentPage_teacher", methods=['GET', 'POST'])
def assignmentPage_teacher():
    selectedAssignment = request.args.get('type')
    assignmentName = selectedAssignment
    selectedCourse = session['selectedCourse']
    session['selectedAssignment'] = selectedAssignment
    folder_path = os.path.join(paraPath, selectedCourse, selectedAssignment)
    
    # only go through student submissions(start with 3)
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

    # conn = sqlite3.connect("tutorial.db")
    # cur = conn.cursor()

    # get grade records
    cur.execute("SELECT studentId, grade FROM grades WHERE courseName=? AND assignment=?", (selected_course, selected_quiz))
    grade_records = cur.fetchall()

    # get ID and grade
    grade_info = [{'studentId': record[0], 'grade': record[1]} for record in grade_records]

    # conn.close()

    return render_template('quizPage_teacher.html', quizName=quiz_name, gradeInfo=grade_info)











@app.route("/courses", methods=['GET', 'POST'])
def courses():
    # check if logged in
    if 'user_id' not in session:
        return "User not logged in"

    # get ID
    user_id = session['user_id']

    # get enrolled courses
    user_courses = cur.execute("SELECT courses FROM users WHERE id = ?", (user_id,)).fetchone()
    if user_courses:
        user_courses = user_courses[0]
    else:
        return "User not found"

    # get all courses
    courseList = cur.execute("SELECT * FROM courses").fetchall()

    if request.method == 'POST':
        student_input = request.form.get("student_input", None)
        if student_input:
            # check if selected course in all courses
            if student_input in user_courses:
                return render_template('courses.html', status="course already selected", courseList=courseList)
            
            # check if appication has been sent before
            existing_applications = cur.execute("SELECT courseName FROM application WHERE studentId = ? AND courseName=?", (user_id,student_input)).fetchall()
            if existing_applications:
                for app_course in existing_applications:
                    if app_course[0] == student_input:
                        return render_template('courses.html', status="application already sent", courseList=courseList)
            
            # check if input is an existing course
            course_exists = cur.execute("SELECT * FROM courses WHERE courseName = ?", (student_input,)).fetchone()
            if not course_exists:
                return render_template('courses.html', status="course does not exist", courseList=courseList)

            # send application
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
#change directory to 'server\course name'
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    """
        upload file
    """
    if request.method == 'POST':
        f = request.files['file']
        
        #change file name to corresponding id
        # f.filename = '123' + os.path.splitext(f.filename)[1]

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
    folder_path = os.path.join(paraPath, course_name)
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
            # con = sqlite3.connect("tutorial.db")
            # cur = con.cursor()
            
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
            # con.close()
            print()
    
    # Fetch instructors whose usernames start with '2'
    users = get_instructors()

    return render_template("createCoursePage.html", users=users)

def get_instructors():
    try:
        # con = sqlite3.connect("tutorial.db")
        # cur = con.cursor()
        cur.execute("SELECT name FROM users WHERE id LIKE '2%'")
        rows = cur.fetchall()
        users = [row[0] for row in rows]
    except sqlite3.Error as e:
        print("Error fetching users:", e)
    finally:
        # con.close()
        print()
        

    return users





@app.route("/AdminRequests", methods=['GET', 'POST'])
def AdminRequests():
    # con = sqlite3.connect('your_database.db')  # Adjust with your actual database path
    # cur = con.cursor()
    applicationList = cur.execute("SELECT * FROM application").fetchall()
    length = len(applicationList)

    if request.method == 'POST':
        try:
            for i in range(length):
                # Check if each application was approved
                if request.form.get(f'approve{i}') is not None:
                    studentId, courseName = applicationList[i][:2]
                    data = (studentId, courseName)

                    # Process the approval
                    cur.execute("DELETE FROM application WHERE studentId=? AND courseName=?", data)

                    studentData = cur.execute("SELECT * FROM users WHERE id=?", (studentId,)).fetchone()
                    stuCourses = studentData[3] + " " + courseName
                    newData = (studentData[0], studentData[1], studentData[2], stuCourses)

                    # Update the users table
                    cur.execute("DELETE FROM users WHERE id=?", (studentId,))
                    cur.execute("INSERT INTO users VALUES(?,?,?,?)", newData)
                    con.commit()
        finally:
            # con.close()
            print("??")

    # Reload the page with updated application list
    applicationList = cur.execute("SELECT * FROM application").fetchall()
    length = len(applicationList)
    return render_template('AdminRequests.html', applicationList=applicationList, length=length)





# @app.route("/dashBoard",methods=['GET','POST'])
# def dashBoard():

#     user=cur.execute("SELECT * FROM users WHERE id=%d"%session['user_id']).fetchone()
#     print(session['user_id'])
#     print(user)
#     courses=user[3].split()
#     role=user[0]
#     if role>3000:
#         roleNum=3#student
#     elif role>2000:
#         roleNum=2#instructor
#     else:
#         roleNum=1#admin
    
#     return render_template('dashBoard.html',courses=courses,roleNum=roleNum)

# @app.route("/coursePage",methods=['GET','POST'])
# def coursePage():
#     selectedCourse=request.args.get('type')
#     session['selectedCourse']=selectedCourse
#     return render_template('coursePage.html')

# @app.route("/assignmentPage",methods=['GET','POST'])
# def assignmentPage():
#     #select which assignment, e.g. A1, A2    
#     course=session['selectedCourse']
#     print(course)
#     assignments=cur.execute("SELECT * FROM assignments WHERE courseName='%s'"%course).fetchall()
#     print(assignments)
#     assignmentList=list()
#     for a in assignments:
#         assignmentList.append(a[1])
#     print(assignmentList)
#     return render_template('assignmentPage.html',assignments=assignmentList)

# @app.route("/assignment",methods=['GET','POST'])
# def assignment():
#     #select which student, e.g. 3001, 3002
#     selectedAssignment=request.args.get('type')
#     session['selectedAssignment']=selectedAssignment
#     studentAssignments=[3001,3002,3003]
#     return render_template('assignment.html',studentAssignments=studentAssignments)

# @app.route("/grading",methods=['GET','POST'])
# def grading():
#     selectedStudent=request.args.get('type')
#     session['selectedStudent']=selectedStudent
    
#     #get instructor input
#     data=(session['selectedCourse'],session['selectedAssignment'],selectedStudent)
#     grade=cur.execute("SELECT grade FROM grades WHERE courseName=? AND assignment=? AND studentId=?",data)
#     try:
#         lock.acquire(True)
#         cur.execute("INSERT INTO grades VALUES(?,?,?,?)",data)
#         con.commit()
#     finally:
#         lock.release()
#     return render_template('grading.html')




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
            # delete old record
            searchData = (courseName, assignmentName, studentId)
            cur.execute("DELETE FROM grades WHERE courseName=? AND assignment=? AND studentId=?", searchData)
            # insert new record
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