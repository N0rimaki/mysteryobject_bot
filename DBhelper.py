#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"


import sqlite3
import logging as dblog
from datetime import datetime

now = datetime.now()
timestamp = datetime.timestamp(now)
time_pretty = str(datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))

LOG_FILENAME_DB = "log_DB.txt"

___debugDB___ = False

if ___debugDB___ == True:
	dblog.basicConfig(filename=LOG_FILENAME_DB,level=dblog.INFO,format='%(message)s')
	
	
def logdb(log_message,created_by,table="logtable",log_levelname="debug"):
	#database = sqlite3.connect('./logDB.db')
	database = sqlite3.connect('logDB.db')
	
	
	c = database.cursor()
	created_at = str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

	try:
		
		c.execute('''INSERT INTO '''+table+''' (log_levelname,log_message,created_at,created_by)VALUES(?,?,?,?)''', (log_levelname,log_message,created_at,created_by))
		
		#sqlstring = "INSERT INTO {0} (log_message,created_at,created_by) VALUES('{1}','{2}',{3}')".format(table,log_message,created_at,created_by)
				
		#c.execute(sqlstring)			  
		
		database.commit()
		return True
	except:
		return False
	finally:
		c.close()

class DBhelper:
	def __init__(self):
		self.database = sqlite3.connect('MOB.sqlite')
		#database = sqlite3.connect('./panminder.db')
		self.c = self.database.cursor()
		return None
	
	def connectDB(self):
		database = sqlite3.connect('MOB.sqlite')
		#database = sqlite3.connect('./panminder.db')
		c = database.cursor()
		return database,c


	
	def CreateTables(database,c):
		c.execute('''CREATE TABLE "Games" (
	"ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"rID"	TEXT UNIQUE,
	"url"	TEXT,
	"status"	INTEGER,
	"solution"	TEXT,
	"author"	TEXT,
	"created_at"	TEXT
);''')
		database.commit()
		c.close()
	
	
	def addNewGame(self,submission):
		
		logdb("in Methode","addNewGame")
		status = '0' #=locked
		created_at = str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
		try:
			self.c.execute('''INSERT OR IGNORE INTO Games(rID,url,status,author,created_at)
						  VALUES(?,?,?,?,?)''', (submission.id,submission.url,status,submission.author.name,created_at))
			self.database.commit()
			sqlquery = self.database.set_trace_callback(print)
			logdb(sqlquery,"addNewGame","info")
			if sqlquery == True:
				
				logdb("insertPost SUCCESS","addNewGame")
				return True
			else:
				
				logdb("insertPost FAIL","addNewGame")
				return False
		except Exception as err:
			
			logdb("Error: "+str(err),"addNewGame","Error")
			return False
		finally:
			logdb("finally","addNewGame")
			#self.c.close()
			
			
	def updateStatus(self,rID,status):
	
		self.c.execute("UPDATE Games SET status = ? WHERE rID = ?",(status,rID))
		self.database.commit()
		logdb("submission "+rID+" locked","updateStatus","info")
		
		
			
	def getSolutionforID(self,rid):
		self.c.execute("Select solution from Games where rID = ? and status = 0",(rid,))
		self.database.commit()
		result = self.c.fetchall()
		return result

		
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			