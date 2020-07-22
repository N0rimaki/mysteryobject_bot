#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"

import praw
import logging as log
import requests
from datetime import datetime
from DBhelper import *
from main import *



class MM:
	
	def __init__(self):
		self.subredditname = 'mysteryobject'
		_UA = 'MOB by /u/[yourouija]'
		reddit = praw.Reddit("bot1",user_agent=_UA)
		reddit.validate_on_submit=True	
		self.r = reddit
		
		self.flair_solved = "882c5aa6-c926-11ea-a888-0e38155ddc41"
		self.flair_running = "7ae507b2-c926-11ea-8bf8-0ef44622e4b7"
		self.flair_onhold = "4aecca10-c99c-11ea-bc5c-0e190f721893"
		
	None
	
	def getDatabase(self,db):
		self.db=db
		return db
	
	def processMessage(self,message):
		my_list = message.body.split(",")
		self.getDatabase(db.updateSolution(message.subject,str(my_list)))
		message.mark_read()
		MO.startGame(self,message.subject)		
		None
		
	def sendMessageNoSolution(self):
		#i cant read your solution, seems there is some issue with formating
		#try again
		None
	
	def streamMessages(self):
		messages = self.r.inbox.stream() # streams inbox
		for message in messages:
			self.processMessage(message)
			
			print(message.author)
			print(message.subject)
			print(message.body)
			
	None


if __name__ == "__main__":
	obj = MM()
	db = DBhelper()
	obj.getDatabase(db)
	obj.streamMessages()
	
	
	
	
	
	