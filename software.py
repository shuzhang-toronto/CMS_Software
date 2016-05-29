import softwareService
import json
import sys
import logging
import time
import kerberos
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

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	
	username = request.form['username']
	password = request.form['password']
	kerberosname = username + '@UTORONTO.CA'
	app.logger.info('%s %s try login', kerberosname, password)
	
	try:
		kerberos.checkPassword(kerberosname, password, '', '')
		session['username'] = request.form['username']
		app.logger.info('[%s] login', session['username'])
		return redirect(url_for('index'))
	except:
		e = sys.exc_info()[0]
		app.logger.info('authenticate error %s', e)
		return render_template('login.html')
	
@app.route('/logout')
def logout():
	if 'username' in session:
		app.logger.info('[%s] logout', session['username'])
		session.pop('username', None)
	return redirect(url_for('index'))
	
@app.route('/query')
def query():
	return jsonify(softwareService.getAllSoftwares2(session['username']))

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
		app.logger.info('[%s] modify %s', user, delta[0])
	
@app.route('/update', methods=['POST'])
def update():
	users = request.json['users']
	softwares = request.json['softwares']
	delta = softwareService.saveAllSoftwares2(users, softwares, session['username'])
	logDelta(session['username'], delta)
	return jsonify({'status':'ok'});
	

handler = RotatingFileHandler('log/test.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
if __name__=="__main__":
	app.run()
