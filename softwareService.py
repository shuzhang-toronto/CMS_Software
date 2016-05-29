import csv
import datetime
from os import listdir, makedirs
from os.path import isfile, join, splitext, exists


def convertUser(user): 
	ret = {} 
	ret['id'] = user[0]
	ret['name'] = user[1]
	ret['email'] = user[2]
	return ret

def getAllUsers(): 
	with open('users.csv', 'r') as csvfile: 
		reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
		users={} 
		for row in reader: 
			users[row[0].strip()] = {'id':row[0].strip(),'name':row[1].strip(),'email':row[2].strip()} 
		return users

def getSoftwaresForUser2(userid):
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

getSoftwaresForUser2('shu')
	
def getSoftwaresForUser(currentuser):
	with open('softwaresUsage.csv', 'r') as csvfile: 
		reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
		userids = [x.strip() for x in next(reader)[1:]]
		idx = -1
		if currentuser in userids:
			idx = userids.index(currentuser)
		
		if idx == -1 :
			return []
		
		softwares = {}
		for row in reader:
			name = row[0]
			usage = [x.strip() for x in row[1:]]
			softwares[name] = usage[idx]
	return softwares
	
def getUsersForSoftware(software):
	allusers = getAllUsers()
	with open('softwaresUsage.csv', 'r') as csvfile: 
		reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
		userids = [x.strip() for x in next(reader)[1:]]
		s = next((x for x in reader if x[0].name == software), None)
		usage = [x.strip() for x in s[1:]]
	
	users = []
	for userid in userids: 
		if userid in allusers: 
			users.append(allusers[userid])
		else: 
			users.append({'id':userid,'name':'','email':''})
	
	ret =[]
	for i in range(len(users)):
		if usage[i]:
			ret.append(users[i])
	return ret

def getAllSoftwares2(currentuser): 	

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


def getAllSoftwares(currentuser): 
	allusers = getAllUsers()
	with open('softwaresUsage.csv', 'r') as csvfile: 
		reader = csv.reader(csvfile, delimiter=',',quotechar='|') 
		userids = [x.strip() for x in next(reader)[1:]]
		idx = -1
		if currentuser in userids:
			idx = userids.index(currentuser)
			userids[0], userids[idx] = userids[idx], userids[0]
		else:
			userids.insert(0, currentuser)
		
		users=[]		
		for userid in userids: 
			if userid in allusers: 
				users.append(allusers[userid])
			else: 
				users.append({'id':userid,'name':'','email':''})

		softwares=[]
		for row in reader:
			name = row[0]
			usage = [x.strip() for x in row[1:]]
			if idx == -1:
				usage.insert(0, '')
			else:
				usage[0], usage[idx] = usage[idx], usage[0]
			softwares.append({'name':name,'usage':usage})

	return {'users':users, 'softwares':softwares}

def saveAllSoftwares2(users, softwares, currentuser):
	exist = getSoftwaresForUser2(currentuser)
	updated = dict([ (x['name'], x['usage'][0]) for x in softwares ])
	changed=[]
	unselected=[]
	selected=[]
	for s in exist:
		if  not s in updated:
			unselected.append(s)
		elif exist[s] != updated[s]:
			changed.append((s, exist[s], updated[s]))
	
	for s in updated:
		if s not in exist:
			selected.append((s, updated[s]))
			
	with open(join('data', currentuser + '.csv'), 'w') as csvfile: 
		writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
		for s in updated:
			if updated[s]:
				writer.writerow([s, updated[s]])
	
	return (changed, unselected, selected)

def getUsersForSoftware2(software):
	data = getAllSoftwares2('')
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
	return [x['email'] for x in getUsersForSoftware2(software)]
	
def export():
	data = getAllSoftwares2('')
	
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

			
def saveAllSoftwares(users, softwares, currentuser):
	exist = getSoftwaresForUser(currentuser)
	updated = dict([ (x['name'], x['usage'][0]) for x in softwares ])
	changed=[]
	unselected=[]
	selected=[]
	for s in exist:
		if  not s in updated:
			unselected.append(s)
		elif exist[s] != updated[s]:
			changed.append((s, exist[s], updated[s]))
	
	for s in updated:
		if s not in exist:
			selected.append((s, updated[s]))
	
	with open('softwaresUsage.csv', 'w') as csvfile: 
		writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
		header = ['software'] + [user['id'] for user in users]
		writer.writerow(header)
		for s in softwares:
			if any(s['usage']):
				writer.writerow([s['name']] + s['usage'])
	
	return (changed, unselected, selected)
