#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"


import sqlite3

from datetime import datetime

now = datetime.now()
timestamp = datetime.timestamp(now)
time_pretty = str(datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))
	
def logdb(log_message,created_by,table="logtable",log_levelname="debug"):
	database = sqlite3.connect('logDB.db')
	c = database.cursor()
	created_at = str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
	try:

		c.execute('''INSERT INTO '''+table+''' (log_levelname,log_message,created_at,created_by)VALUES(?,?,?,?)''', (log_levelname,log_message,created_at,created_by))
		database.commit()
		return True
	except:
		return False
	finally:
		#c.close()
		None
		
class DBhelper:
	def __init__(self):
		#self.database = sqlite3.connect('/home/pi/mysteryobject_bot/MOB.sqlite')
		self.database = sqlite3.connect('MOB.sqlite')
		self.c = self.database.cursor()
		self.created_at = str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
		return None


	def CreateTables(database,c):
		c.execute('''CREATE TABLE "Games" (
	"ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"rID"	TEXT UNIQUE,
	"title"	TEXT,
	"permalink"	TEXT,
	"status"	INTEGER,
	"solution"	TEXT,
	"author"	TEXT,
	"created_at"	TEXT
);''')
		database.commit()
		c.close()
		
		k='''CREATE TABLE "statistics" (
	"ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"authorname"	TEXT,
	"permalink"	TEXT,
	"title"	TEXT,
	"created_at"	TEXT
);'''
	
	
	def addNewGame(self,submission):
		
		#logdb("in Methode","addNewGame")
		status = '0' #=locked
		perm = "https://www.reddit.com"+submission.permalink
		try:
			self.c.execute('''INSERT OR IGNORE INTO Games(rID,title,permalink,status,author,created_at)
						  VALUES(?,?,?,?,?,?)''', (submission.id,submission.title,perm,status,submission.author.name,self.created_at))
			self.database.commit()
			sqlquery = self.database.set_trace_callback(None)
			#logdb(sqlquery,"addNewGame","info")
			if sqlquery == True:
				
				#logdb("insertPost SUCCESS","addNewGame")
				return True
			else:
				
				#logdb("insertPost FAIL","addNewGame")
				return False
		except Exception as err:
			
			#logdb("Error: "+str(err),"addNewGame","Error")
			return False
		finally:
			None#logdb("finally","addNewGame")
			#self.c.close()
		
		
	def addWinner(self,authorname,permalink,title):
		#logdb("in Methode","addWinner","info")

		self.c.execute('''INSERT INTO statistics (authorname,permalink,title,created_at)
					  VALUES(?,?,?,?)''', (authorname,permalink,title,self.created_at))
		self.database.commit()
	
	
	def updateStatus(self,rID,status):
	
		self.c.execute("UPDATE Games SET status = ? WHERE rID = ?",(status,rID))
		self.database.commit()
		#logdb("submission "+rID+" locked","updateStatus","info")
		
	
	def getSolutionforID(self,rid):
		self.c.execute("Select solution from Games where rID = ? and status = 0",(rid,))
		self.database.commit()
		result = self.c.fetchall()
		return result
	
	
	def getSolvedbyUser(self,authorname):
		self.c.execute("Select count() as counter from statistics where authorname = ?",(authorname,))
		self.database.commit()
		result = self.c.fetchall()
		return result

	def getCreatedbyUser(self,authorname):
		self.c.execute("Select count() as counter from Games where authorname = ?",(authorname,))
		self.database.commit()
		result = self.c.fetchall()
		return result

	def updateSolution(self,permalink,solution):
		logdb("in Methode","updateSolution","info")

		self.c.execute("UPDATE Games SET solution = ? WHERE rID = ?",(solution,permalink))
		self.database.commit()	
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			