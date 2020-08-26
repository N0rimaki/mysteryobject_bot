#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"


import sqlite3
from datetime import datetime



created_at = str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))		
class DBhelper:
	def __init__(self):
		
		self.database = sqlite3.connect('/home/pi/mysteryobject_bot/mysterydb.db')
		self.c = self.database.cursor()
		
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
	"author"	TEXT,
	"permalink"	TEXT,
	"title"	TEXT,
	"created_at"	TEXT
);'''
	
	
	def addNewGame(self,submission):
		status = '0' #=locked
		perm = "https://www.reddit.com"+submission.permalink
		try:
			self.c.execute('''INSERT OR IGNORE INTO Games(rID,title,permalink,status,author,created_at)
						  VALUES(?,?,?,?,?,?)''', (submission.id,submission.title,perm,status,submission.author.name,created_at))
			self.database.commit()
			sqlquery = self.database.set_trace_callback(None)
			if sqlquery == True:
				
				return True
			else:
				
				return False
		except Exception as err:
			
			return False
		finally:
			None



	def newTime(self):	
		now = datetime.now()
		self.timestamp = datetime.timestamp(now)

	def addWinner(self,author,permalink,title):
		self.c.execute('''INSERT INTO statistics (author,permalink,title,created_at)
					  VALUES(?,?,?,?)''', (author,permalink,title,created_at))
		self.database.commit()
	
	
	def updateStatus(self,rID,status):
	
		self.c.execute("UPDATE Games SET status = ? WHERE rID = ?",(status,rID))
		self.database.commit()
	
	def updateTimestamp_start(self,rID):
		self.newTime()
		self.c.execute("UPDATE Games SET timestamp_start = ? WHERE rID = ?",(self.timestamp,rID))
		self.database.commit()	

	def updateTimestamp_stop(self,rID):
		self.newTime()
		self.c.execute("UPDATE Games SET timestamp_stop = ? WHERE rID = ?",(self.timestamp,rID))
		self.database.commit()	
	
	def getTimestamps(self,rid):
		self.c.execute("Select timestamp_start,timestamp_stop from Games where rID = ? ",(rid,))
		self.database.commit()
		result = self.c.fetchall()
		return result		
	
	def getSolutionforID(self,rid):
		self.c.execute("Select solution from Games where rID = ? and status in (0,2)",(rid,))
		#self.c.execute("Select solution from Games where rID = ?",(rid,))
		self.database.commit()
		result = self.c.fetchall()
		return result
	
	
	def getSolvedbyUser(self,author):
		self.c.execute("Select count() as counter from statistics where author = ?",(author,))
		self.database.commit()
		result = self.c.fetchall()
		return result

	def getCreatedbyUser(self,authorname):
		self.c.execute("Select count() as counter from Games where author = ?",(authorname,))
		self.database.commit()
		result = self.c.fetchall()
		return result	
	
	def getLeaderboard(self):
		self.c.execute("Select author,count() as counter from statistics GROUP by author order by counter desc")
		self.database.commit()
		result = self.c.fetchall()
		return result

	def updateSolution(self,permalink,solution):
		self.c.execute("UPDATE Games SET solution = ? WHERE rID = ?",(solution,permalink))
		self.database.commit()	
			
	def getHintcount(self,rid):
		self.c.execute("Select hintcount,solution,status from Games WHERE rID = ?",(rid,))
		self.database.commit()
		result = self.c.fetchall()
		return result

	def updateHintcount(self,rid):
		self.c.execute("UPDATE Games SET hintcount = hintcount + 1 WHERE rID = ?",(rid,))
		self.database.commit()				
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			