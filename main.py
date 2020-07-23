#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"

import praw
import os
from datetime import datetime
import configparser
import logging as log
from DBhelper import *
from main_messages import *

now = datetime.now()
timestamp = datetime.timestamp(now)
timeMinusOneDay = timestamp-(24*60*60)

LOG_FILENAME = "./log_Main.log"


___debug___ = True
___runprod___= False

if ___debug___ == True:
		log.basicConfig( handlers=[
            log.FileHandler(LOG_FILENAME),
            log.StreamHandler()],level=log.INFO,format='%(asctime)s : %(levelname)s : %(message)s')



class MO:
	
	def __init__(self):
		self.subredditname = 'mysteryobject'
		_UA = 'MOB by /u/[yourouija]'
		try:
			reddit = praw.Reddit("bot1",user_agent=_UA)
			reddit.validate_on_submit=True	
			self.r = reddit
		except Exception as err:
			log.error("__init__() ",str(err))
			self.rebootClass(err)
			
			
		self.flair_solved = "882c5aa6-c926-11ea-a888-0e38155ddc41"
		self.flair_running = "7ae507b2-c926-11ea-8bf8-0ef44622e4b7"
		self.flair_onhold = "4aecca10-c99c-11ea-bc5c-0e190f721893"
		
		log.info("init Main Bot Class")	
		None
	
	
	def getDatabase(self,db):
		self.db=db
		return db
		
		
		
	def closeGame(self,rid,reason):
		submission = self.r.submission(id=rid)
		#setFlair
		if reason == 1:
			submission.flair.select(self.flair_solved)
		elif reason == 2:
			submission.flair.select(self.flair_onhold)
				
		#LockThread
		submission.mod.lock()
		#comment winner comment, done in main_messages.py
		log.info("Game closed %s %s %s",submission.author.name,submission.id, submission.title)	

		None
	
	def startGameGateway(rid):
		self.startGame(rid)
		None
	
	def startGame(self,message,solution=None):
		submission = self.r.submission(id=message.subject)
		#setFlair
		submission.flair.select(self.flair_running)
		#unLockThread
		submission.mod.unlock()
		#send message to creator that puzzle has started? Nope
		log.info("Game started %s %s %s %s",submission.author.name,submission.id,submission.title,str(solution))	

		None
	
	def check24h(self,id):
		#when no reply after 24h delte the submission
		#set flair locked
		#remove submission
		None

	def processComment(self,comment):
		#Here we analyze the comment and compare user comment with databasesolution
		parent_ID = comment.parent_id.replace('t3_','')
		
		ss = self.getDatabase(db.getSolutionforID(parent_ID))
		for s in ss:
			solution = str(s[0])
		
			
			if comment.body.lower()  in solution.lower():
				
				self.madeWinnerComment(comment,parent_ID,solution)
				self.closeGame(parent_ID,1)
				self.getDatabase(db.updateStatus(parent_ID,1))
				self.getDatabase(db.addWinner(comment.author.name,comment.submission.permalink,comment.submission.title))
				self.updateUserFlair(comment.author.name)
				
				log.info("Solution found: %s %s %s",parent_ID,comment.submission.title,comment.body)	
			
	
	
	def updateUserFlair(self,authorname):
		#count how many puzzles the person solved
			#update the flair Solved:xx
		solved = self.getDatabase(db.getSolvedbyUser(authorname))
		flairtext = ""
		
		for r in solved:
			if r[0] >= 1:
				flairtext="solved:"+str(r[0])
		
		created = self.getDatabase(db.getCreatedbyUser(authorname))
		for c in created:
			if c[0] >=1:
				flairtext = flairtext+"|created:"+str(c[0])
				
		self.r.subreddit(self.subredditname).flair.set(authorname, flairtext)
		log.info("Userflair changed %s %s",authorname,flairtext)	

		None
	
	def madeWinnerComment(self,comment,parent_ID,solution):
		#reply that user have won
		comment.reply("you win this round")
		user = comment.author.name
		#made mod submission with winner
		submission = self.r.submission(id=parent_ID)
		modcommentid = submission.reply("IAM THE LAW - User r/"+user+" has won the round.\n\rOPs solutions: "+solution)
		#made mod comment sticky 
		comment = self.r.comment(modcommentid)
		comment.mod.distinguish(how="yes", sticky=True)		
		log.info("did the winner comment")	
		None
		
	def getMessages(self):
		#done in main_messages.py
		None
	def sendMessageNoSolution(self):
		#done in main_messages.py
		None
	def sendMessageSuccesfullSolved(self):
		#Your puzzle ID has solved by 
		#wontdothis
		None
		
	
	def sendAuthorWelcomeMessage(self):
		#Done by Automoderator
		None
		
	def initialComment(self,rid):
		#upvote this comment to get a hint
		#10 updoots post first and last letter X......xrange

		#made mod submission with winner
		submission = self.r.submission(id=rid)
		modcommentid = submission.reply("Post what you guess the object in the picture could be, just comment the picture.")
		#made mod comment sticky 
		comment = self.r.comment(modcommentid)
		comment.mod.distinguish(how="yes", sticky=True)		
		log.info("create inital comment")	
		


	
	def streamAll(self):
		comment_stream = self.r.subreddit(self.subredditname).stream.comments(pause_after=-1)
		submission_stream = self.r.subreddit(self.subredditname).stream.submissions(pause_after=-1)
		while True:
			try:
				for comment in comment_stream:
					if comment is None:
						break
					#if some comment is found, it enter here the processing of the comment
					self.processComment(comment)
					
				for submission in submission_stream:
					if submission is None:
						break
	
					#here we monitor for new submissions
					self.getDatabase(db.addNewGame(submission))	
					self.initialComment(submission.id)
					self.updateUserFlair(submission.author.name)
					log.info("new Game detected: %s, %s, %s",submission.author.name,submission.title, submission.link_flair_text)

			except Exception as err:
				log.error("streamall() ",str(err))
				self.rebootClass(err)
	
	
	def rebootClass(self,err):
		log.error("FATAL, restart class %s",str(err))	
		os.system("python main.py")	
	
	
	
if __name__ == "__main__":			
	obj = MO()
	db= DBhelper()
	obj.getDatabase(db)
	obj.streamAll()
	


