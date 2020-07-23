#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"

import os
import praw
import logging as log
import requests
from DBhelper import *
from main import *

LOG_FILENAME_message = "./log_Messages.log"


___debug___ = True
___runprod___= False

if ___debug___ == True:
	log.basicConfig( handlers=[
            log.FileHandler(LOG_FILENAME_message),
            log.StreamHandler()],level=log.INFO,format='%(asctime)s : %(levelname)s : %(message)s')


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
		log.info("init Main Message Class")	
		None
	
	def getDatabase(self,db):
		self.db=db
		return db
	
	def processMessage(self,message):
		try:
			my_list = message.body.split(",")
			self.getDatabase(db.updateSolution(message.subject,str(my_list)))
			message.mark_read()
			MO.startGame(self,message,my_list)		
		except Exception as err:
			log.error("something wrong processMessage(): ",str(err))	
			self.rebootClass()
		None
		
	def sendMessageNoSolution(self):
		#i cant read your solution, seems there is some issue with formating
		#try again
		None
	
	def streamMessages(self):
		try:
			messages = self.r.inbox.stream() # streams inbox
			for message in messages:
				self.processMessage(message)
				
				log.info("Message recieved: %s %s %s",message.author,message.subject,message.body)	
				
		except Exception as err:
			log.error("something wrong streamMessages(): ",str(err))	
			self.rebootClass()
			
		None
	
	def rebootClass(self):
		log.error("FATAL, restart class")	
		os.system("python main_messages.py")


if __name__ == "__main__":
	obj = MM()
	db = DBhelper()
	obj.getDatabase(db)
	obj.streamMessages()
	
	
	
	
	
	