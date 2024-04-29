# Soul, an E-learning platform
Step-by-step Guide
1.	Download the project(Soul).
2.	Create a Python virtual environment. https://docs.python.org/3/library/venv.html
3.	Install Flask using the command: pip install FLASK(windows&ios)
   ![alt text](https://github.com/COSC310-Soul-team/Soul//blob/main/screen%20shots/flask.png?raw=true)
5.	Activate the virtual environment by enter scripts/bin and run the command “activate”.
6.	Go to the directory of Soul.
7.	Change the global path variable path1 & paraPath to local sever folder in app.py.
8.	Run dbTest.py to connect to the database and create tables.
9.	Under the virtual environment, run “flask run” to start the server.
 the server is now running on http://127.0.0.1:5000, going to http://127.0.0.1:5000/login on a browser, you will see the login page 

Maintenance: 
1.	The database is local, deleting the database file(tutorial.db) will delete the whole database.
2.	Running dbTest.py will drop all the tables and create new empty tables.
3.	The server keeps track of the users, stopping the server will make the system malfunction.
