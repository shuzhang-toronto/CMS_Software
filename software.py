import softwareService
import emailService
import json
import sys
import logging
import time
#import kerberos
from logging.handlers import RotatingFileHandler
from flask import Flask, session, jsonify, g, redirect, request, render_template, url_for, send_file

app = Flask(__name__)
app.debug = True
app.secret_key = 'A1Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.kerberosRealm = '@UTORONTO.CA'
	
@app.route('/')
def index():
	if not 'username' in session:
		return redirect(url_for('login'))
	return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
	if not 'username' in session:
		return redirect(url_for('login'))
	
	fullname = request.form['fullname']
	email = request.form['email']
	#softwareService.updateUser(session['username'], fullname, email)
	return redirect(url_for('index'))
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		allusers = softwareService.getAllUsers()
		if username not in allusers:
			error = "'" + username + "' is not entitled for this application"
		else:
			password = request.form['password']
			kerberosname = username + '@UTORONTO.CA'
			app.logger.info('%s %s try login', kerberosname, password)
	
			try:
#				kerberos.checkPassword(kerberosname, password, '', '')
				session['username'] = request.form['username']
				app.logger.info('[%s] login', session['username'])
				
				fullname = allusers[username]["name"]
				email = allusers[username]["email"]
				if fullname and email:
					return redirect(url_for('index'))
				else:
					return render_template('register.html', id=username, name=fullname, email=email)
			except:
				e = sys.exc_info()[0]
				app.logger.info('authenticate error %s', e)
				error = "invalid credential"
		
	return render_template('login.html', error=error)
	
@app.route('/logout')
def logout():
	if 'username' in session:
		app.logger.info('[%s] logout', session['username'])
		session.pop('username', None)
	return redirect(url_for('index'))
	
@app.route('/query')
def query():
	return jsonify(softwareService.getSoftwaresUsage(session['username']))

@app.route('/export')
def export():
	path = softwareService.export()
	return send_file(path,
                     mimetype='text/csv',
                     attachment_filename='softwareUsages.csv',
                     as_attachment=True)
	
def logDelta(user, delta):
	if delta[1]:
		app.logger.info('[%s] deselect %s', user, delta[1])
	if delta[2]:
		app.logger.info('[%s] select %s', user, delta[2])
	if delta[0]:
		app.logger.info('[%s] add new software %s', user, delta[0])

def sendEmail(user, delta):
	subject = "CMS software change request"
	msg = "UserId: " + user + "\r\n"
	if delta[1]:
		msg += 'select ' + ';'.join(delta[1])
	if delta[2]:
		msg += 'unselect ' + ';'.join(delta[2])
	if delta[0]:
		msg += 'add new software ' + ';'.join(delta[0])
		
	to='zhangdog@hotmail.com'
	me='zhangdog@gmail.com'
	
	emailService.sendEmail(me, to, subject, msg)
	
@app.route('/update', methods=['POST'])
def update():
	users = request.json['users']
	softwares = request.json['softwares']
	delta = softwareService.saveAllSoftwares(users, softwares, session['username'])
	logDelta(session['username'], delta)
	sendEmail(session['username'], delta)
	return jsonify({'status':'ok'});	

handler = RotatingFileHandler('log/test.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
if __name__=="__main__":
	app.run()