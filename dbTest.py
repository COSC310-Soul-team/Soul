import sqlite3

con = sqlite3.connect("tutorial.db",check_same_thread=False)
cur = con.cursor()
cur.execute("DROP TABLE users")
cur.execute("DROP TABLE application")
cur.execute("DROP TABLE courses")
cur.execute("DROP TABLE assignment")
cur.execute("DROP TABLE quiz")
cur.execute("CREATE TABLE courses(courseName,instructor)")
cur.execute("CREATE TABLE application(studentId,courseName)")
cur.execute("CREATE TABLE users(id,name,password,courses)")
cur.execute("CREATE TABLE grades(courseName,assignment,studentId,grade)")
cur.execute("CREATE TABLE assignment(assignmentName,courseName)")
cur.execute('''CREATE TABLE quiz (
               QuizName TEXT,
               Course TEXT,
               QuizNumber INTEGER,
               Question TEXT,
               OptionA TEXT,
               OptionB TEXT,
               OptionC TEXT,
               OptionD TEXT,
               Answer TEXT)''')
con.commit() 