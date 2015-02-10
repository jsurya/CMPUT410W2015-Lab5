import sqlite3
from flask import Flask, render_template, g, flash, session, redirect, request, url_for, abort

DATABASE = 'test.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'This is secret!'

app = Flask(__name__)
app.config.from_object(__name__)		# given object

@app.route('/')
def welcome():
	return '<h1>Welcome to CMPUT 410 - Jinja Lab!</h1>'

@app.route('/task', methods = ['GET', 'POST'])
def task():
	if request.method == 'POST':
		if not session.get('logged_in'): 
			abort(401)		# authentication error
		category = request.form['category']
		priority = request.form['priority']
		description = request.form['description']
		
		addTask(category, priority, description)
		flash('New task was successfully added')
		return redirect(url_for('task'))
	return render_template('show_entries.html', tasks = query_db('select * from tasks'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You are logged in...')
			return redirect(url_for('task'))
	return render_template('login.html', error = error)

@app.route('/logout', methods = ['GET'])
def logout():
	session.pop('logged_in', None)
	flash('You are logged out...')
	return redirect(url_for('task'))

@app.route('/delete', methods = ['POST'])
def delete():
	if not session.get('logged_in'):
		abort(401)		# authenitication failed

	if request.method == 'POST':
		for task in request.form:
			removeTask(task)
	flash('Task deleted')
	return redirect(url_for('task'))
	
def removeTask(task):
	query_db('DELETE FROM tasks WHERE task_id = ?', [task], one = True)
	get_db().commit()

def addTask(category, priority, description):
	query_db('INSERT  INTO tasks (category, priority, description) VALUES (?, ?, ?)',
	 [category, int(priority), description], one = True)
	get_db().commit()

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
		db.row_factory = sqlite3.Row 
	return db

@app.teardown_appcontext
def close_conn():
	db = getattr(g, '_database', None)
	if db is not None:
		db.close

def query_db(query, args = (), one = False):
	cur = get_db().cursor()
	cur.execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

if __name__ == '__main__':
	# interpreter is using this file directly
	app.debug = True
	app.run()