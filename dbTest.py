import sqlite3

con = sqlite3.connect("tutorial.db",check_same_thread=False)
cur = con.cursor()
user = cur.execute("SELECT * FROM users").fetchone()
print(user)