import sqlite3

con = sqlite3.connect("tutorial.db",check_same_thread=False)
cur = con.cursor()
# cur.execute("DROP TABLE users")
# cur.execute("DROP TABLE application")
# cur.execute("DROP TABLE courses")
cur.execute("CREATE TABLE courses(courseName,assignments,members)")
cur.execute("CREATE TABLE application(studentId,courseName)")
cur.execute("CREATE TABLE users(id,name,password)")
con.commit()