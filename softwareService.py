import csv
import datetime
from time import time
from os import listdir, makedirs, remove, stat
from os.path import isfile, join, splitext, exists

def getAllSoftwares():
	try:
		with open('config/softwares.csv', 'r') as csvfile: 
			reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
			all = set()
			for row in reader: 
				all.add(row[0].strip())
			return all
	except IOError:
		return set()
	
def getAllUsers(): 
	with open('config/users.csv', 'r') as csvfile: 
		reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
		users={} 
		for row in reader: 
			users[row[0].strip()] = {'id':row[0].strip(),'name':row[1].strip(),'email':row[2].strip()} 
		return users

def updateUser(id, name, email):
	while True:
		if not exists('config/userdilelock'):
			lock = open('config/userdilelock', 'w')
			with open('config/users.csv', 'r') as csvfile: 
				reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
				users = []
				update = []
				for row in reader: 
					if row[0].strip() != id.strip():
						users.append(tuple(row))
					else:
						ln = len(row)
						update.append(row[0].strip())
						if name:
							update.append(name.strip())
						elif ln > 1 and row[1].strip():
							update.append(row[1].strip())
						else:
							update.append("")
							
						if email:
							update.append(email.strip())
						elif ln > 2 and row[2].strip():
							update.append(row[2].strip())
						else:
							update.append("")
						users.append(tuple(update))
			
			with open("config/users.csv", 'w') as csvfile: 
				writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
				write.writerows(users)
			lock.close()
			remove('config/userdilelock')
			return
		else:
			check = stat('config/userdilelock')
			if time() - check.st_ctime > 0.01: 
				remove('config/userdilelock')
		
def getSoftwaresForUser(userid):
	mypath='data'
	path=join(mypath, userid + '.csv')
	if not isfile(path):
		return {}
	
	softwares = {}
	with open(path, 'r') as csvfile: 
		reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
		for row in reader:
			if len(row) > 1:
				notes = row[1].strip()
			else:
				notes = 'x'
			softwares[row[0].strip()] = notes
	return softwares

def getSoftwaresUsage(currentuser): 	

	allusers = getAllUsers()

	mypath='data'
	userids = [splitext(f)[0] for f in listdir(mypath) if isfile(join(mypath, f)) and splitext(f)[1] == '.csv']
	if currentuser:
		if currentuser in userids:
			idx = userids.index(currentuser)
			userids[0], userids[idx] = userids[idx], userids[0]
		else:
			userids.insert(0, currentuser)
	
	users = []
	allsoftwares = {}
	for userid in userids:
		if userid in allusers: 
			users.append(allusers[userid])
		else: 
			users.append({'id':userid,'name':userid,'email':''})
		
		path = join(mypath, userid + '.csv')
		if isfile(path):
			with open(path, 'r') as csvfile: 
				reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
				softwares = list(reader)
			
			for software in softwares:
				if len(software) > 1:
					notes = software[1]
				else:
					notes = 'x'
				if software[0] in allsoftwares:
					allsoftwares[software[0]][userid] = notes
				else:
					allsoftwares[software[0]] = { userid:notes }
	
	softwares = []
	for software in allsoftwares:
		usage = []
		for userid in userids:
			if userid in allsoftwares[software]:
				usage.append(allsoftwares[software][userid])
			else:
				usage.append('')
		softwares.append({'name':software, 'usage':usage})
		
	return {'users':users, 'softwares':softwares}

def saveAllSoftwares(users, softwares, currentuser):
	exist = set(getSoftwaresForUser(currentuser).keys())
	updated = set([ x['name'] for x in softwares if x['usage'][0]])
	
	with open(join('data', currentuser + '.csv'), 'w') as csvfile: 
		writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
		for s in updated:
				writer.writerow((s,))
	all = getAllSoftwares()
	new = updated - all
	if(len(new) > 0):
		while True:
			if not exists('config/softwarelock'):
				lock = open('config/softwarelock', 'w')
				with open('config/softwares.csv', 'w') as csvfile: 
					writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
					for s in new | all:
						writer.writerow((s,))
				lock.close()
				remove('config/softwarelock')
				break
			else:
				check = stat('config/softwarelock')
				if time() - check.st_ctime > 0.01: 
					remove('config/softwarelock')

	return (new, updated - exist - new, exist - updated)

def getUsersForSoftware(software):
	data = getSoftwaresUsage('')
	lst = [s for s in data['softwares'] if s['name'] == software]
	count = len(lst)
	if count != 1:
		return []
	
	idx = 0
	users = []
	for usage in lst[0]['usage']:
		if usage:
			users.append(data['users'][idx])
		idx += 1
		
	return users

def getEmailsForSoftware(software):
	return [x['email'] for x in getUsersForSoftware(software)]
	

def export():
	data = getAllSoftwares('')
	
	exp =[]
	exp.append(['software'] + [u['id'] for u in data['users']])
	for software in data['softwares']:
		exp.append([software['name']] + software['usage'])
	
	directory = 'export'
	if not exists(directory):
		makedirs(directory)
	filename = "".join(['softwareUsage', datetime.datetime.now().strftime("_%y%m%d_%H%M%S"), '.cvs']) 
	path = join(directory, filename)
	with open(path, 'w') as csvfile: 
		writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
		writer.writerows(exp)
	
	return path

