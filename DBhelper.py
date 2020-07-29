#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"


import sqlite3
from datetime import datetime


		
class DBhelper:
	def __init__(self):
		
		self.database = sqlite3.connect('mysterydb.db')
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
						  VALUES(?,?,?,?,?,?)''', (submission.id,submission.title,perm,status,submission.author.name,self.created_at))
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
		
		
	def addWinner(self,author,permalink,title):
		self.c.execute('''INSERT INTO statistics (author,permalink,title,created_at)
					  VALUES(?,?,?,?)''', (author,permalink,title,self.created_at))
		self.database.commit()
	
	
	def updateStatus(self,rID,status):
	
		self.c.execute("UPDATE Games SET status = ? WHERE rID = ?",(status,rID))
		self.database.commit()
		
		
	
	def getSolutionforID(self,rid):
		self.c.execute("Select solution from Games where rID = ? and status = 0",(rid,))
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
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			