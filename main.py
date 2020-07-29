#!/usr/bin/python3
__author__ = "u/wontfixit"
__copyright__ = "Copyright 2020"
__license__ = "GPL"
__version__ = "1.0.0"

import praw
import os
import re
import ast
from datetime import datetime
import configparser
import logging as log
from DBhelper import *
from messages import *
import time

now = datetime.now()
timestamp = datetime.timestamp(now)
timeMinusOneDay = timestamp-(24*60*60)

LOG_FILENAME = "./log_main.log"


___debug___ = True
___runprod___= True

if ___debug___ == True:
		log.basicConfig( handlers=[
            log.FileHandler(LOG_FILENAME),
            log.StreamHandler()],level=log.INFO,format='%(asctime)s ; %(levelname)s ; %(funcName)s() ; %(message)s')



class MO:
	
	def __init__(self):
		self.subredditname = 'mysteryobject'
		_UA = 'MOB by /u/[yourouija]'
		try:
			reddit = praw.Reddit("bot1",user_agent=_UA)
			reddit.validate_on_submit=True	
			self.r = reddit
		except Exception as err:
			log.error("Exception {}".format(str(err)))
			self.rebootClass(err)
				
		self.flair_solved = "882c5aa6-c926-11ea-a888-0e38155ddc41"
		self.flair_running = "7ae507b2-c926-11ea-8bf8-0ef44622e4b7"
		self.flair_onhold = "4aecca10-c99c-11ea-bc5c-0e190f721893"
		
		log.info("Starting the Bot Class, omg i'm nervous")	
		None
	
	
	def getDatabase(self,db):
		#get Database obj and pass it
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
		log.info("Game closed {} {} {}".format(submission.author.name,submission.id, submission.title))	

		None
	
	
	def startGame(self,message,solution=None):
		submission = self.r.submission(id=message.subject)
		#setFlair
		submission.flair.select(self.flair_running)
		#unLockThread
		submission.mod.unlock()
		#send message to creator that puzzle has started? Nope
		log.info("Game started  {} {} {} {}".format(submission.author.name,submission.id,submission.title,str(solution)))	
		None


	def processCommentSingleWord(self,comment):
		#Here we analyze the comment and compare user comment with databasesolution
		parent_ID = comment.parent_id.replace('t3_','')
		
		ss = self.getDatabase(db.getSolutionforID(parent_ID))
		
		for s in ss:
			solution = str(s[0])
			tmpsolution = solution.lower()
			
			try:
				tmpsolution = ast.literal_eval(tmpsolution)
				tmpsolution = [n.strip() for n in tmpsolution]
			except Exception as err:
				log.error("string to list: {}".format(str(err)))			
			
			userguess = re.sub(r"[^A-Za-z0-9ÄäÖöÜü$€¥£¢₧ƒ\- ]","",comment.body.lower().strip())

			log.info("User: {} try {} = {} on {}".format(comment.author.name,userguess,tmpsolution,parent_ID))

			if [s for s in tmpsolution if s in userguess]:

			#if comment.body.lower()  in tmpsolution:
				if ___runprod___ == True:	
					self.madeWinnerComment(comment,parent_ID,tmpsolution)
					self.closeGame(parent_ID,1)
					self.getDatabase(db.updateStatus(parent_ID,1))
					self.getDatabase(db.addWinner(comment.author.name,comment.submission.permalink,comment.submission.title))
					self.updateUserFlair(comment.author.name)
					self.updateLeaderboard()
				else:
					log.info("RUN only in DEMO mode, no changes were made at the submission.")
				
				
				log.info("Solution found: {} {} {}".format(parent_ID,comment.submission.title,comment.body))
	
	
	
	def processCommentMutlipleWords(self,comment):
		#Here we analyze the comment and compare user comment with databasesolution
		parent_ID = comment.parent_id.replace('t3_','')
		
		ss = self.getDatabase(db.getSolutionforID(parent_ID))
		
		for s in ss:
			solution = str(s[0])
			tmpsolution = solution.lower()
			
			try:
				tmpsolution = ast.literal_eval(tmpsolution)
				tmpsolution = [n.strip() for n in tmpsolution]
			except Exception as err:
				log.error("string to list: {}".format(str(err)))			
			
			userguess = re.sub(r"[^A-Za-z0-9ÄäÖöÜü$€¥£¢₧\- ]","",comment.body.lower().strip()).split(' ')
			
			prettytime = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
			log.info("User: {} at {} try \"{}\" = {} on {}".format(comment.author.name,prettytime,userguess,tmpsolution,parent_ID))

			#for solutionword in tmpsolution:
			checktuple = self.checkSolution(userguess,tmpsolution)
			if checktuple[0]:
				if ___runprod___ == True:
					self.madeWinnerComment(comment,parent_ID,tmpsolution)
					self.closeGame(parent_ID,1)
					self.getDatabase(db.updateStatus(parent_ID,1))
					self.getDatabase(db.addWinner(comment.author.name,comment.submission.permalink,comment.submission.title))
					self.updateUserFlair(comment.author.name)
					self.updateLeaderboard()
				else:
					log.info("RUN only in DEMO mode, no changes were made at the submission.")
				
				
				log.info("Solution found: {} {} {} {} {}".format(parent_ID,comment.submission.title,str(checktuple[1]),str(tmpsolution),str(userguess)))
	
	def checkSolution(self,userguess,solution):
		#check if the guess of the user is includet in the solution
		#this works very well, because booth are lists and compare word==word
		# with for x in y you get matches you dont want
		c = set(userguess).intersection(set(solution))
		return bool(c),c
		
		
	def updateUserFlair(self,authorname):
		#count how many puzzles the person solved
		#update the flair solved:XX|created:XX
		if authorname != 'wontfixit':
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
			log.info("Userflair changed {} {}".format(authorname,flairtext))
			None
	
	def madeWinnerComment(self,comment,parent_ID,solution):
		#reply that user have won
		comment.reply("you win this round")
		user = comment.author.name
		#made mod submission with winner
		submission = self.r.submission(id=parent_ID)
		modcommentid = submission.reply("I AM THE LAW - User u/"+user+" has won the round.\n\rOPs solutions: "+str(solution))
		#made mod comment sticky 
		comment = self.r.comment(modcommentid)
		comment.mod.distinguish(how="yes", sticky=True)		
		log.info("Bot answered the winner comment from {}".format(comment.author.name))	
		None
		

	def streamAll(self):
	
		start_time = time.time()
		start_time = start_time-300
		log.info("Getting Posts not older than {}".format(str(time.ctime(start_time))))
		
		
		comment_stream = self.r.subreddit(self.subredditname).stream.comments(pause_after=-1)
		submission_stream = self.r.subreddit(self.subredditname).stream.submissions(pause_after=-1)
		while True:
			try:
				for comment in comment_stream:
					
					if comment is None:
						break
					if comment.created_utc < start_time:
						continue
					if comment.author.name != 'AutoModerator':	
						#if some comment is found, it enter here the processing of the comment
						self.processCommentMutlipleWords(comment)
					
				for submission in submission_stream:
					if submission is None:
						break
					if submission.created_utc < start_time:
						continue
					#regex for only do some action when picture submission is detected, i bet there is some better methode	
					regex = r"https:\/\/i\.redd\.it|https:\/\/i\.imgur\.com"
					if re.search(regex, submission.url, re.MULTILINE):
						log.info("IMAGE found")	
						
						if ___runprod___ == True:
							#here we monitor for new submissions
							self.getDatabase(db.addNewGame(submission))	
							#self.initialComment(submission.id)
							self.updateUserFlair(submission.author.name)
						else:
							log.info("RUN only in DEMO mode, no changes were made at the submission.")
							
					else:
						log.info("no Image found")
					
					prettytime = datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')	
					log.info("Submission detected: {},{},{},{},{}".format(prettytime,submission.author.name,submission.title,submission.link_flair_text,submission.url))

			except Exception as err:
				log.error("Exception {} ".format(str(err)))
				self.rebootClass(err)
	
	
	
	def updateLeaderboard(self):
		styles = {"backgroundColor": "#FFFF66", "headerColor": "#3333EE"}
		widgets = self.r.subreddit(self.subredditname).widgets
		new_text = self.getDatabase(db.getLeaderboard())
		
		row_text = "Rank|username|solved\r\n---|---|---\r\n"
	
		i=1
		for row in new_text:
			row_text += str(i)+"|"+str(row[0])+"|"+str(row[1])+"\r\n"
			
			i=i+1
		#print(row_text)
		
		try:
			for widget in widgets.sidebar:
				widget.mod.update(shortName="Leaderboard",text=row_text)
				log.info("done")
		except Exception as err:
			log.error("Exception {}".format(str(err)))
	None
	
	############# functions: abdoned, automod, todo, wontdo
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
		#rules for Author
		#done by AutomMderator
		None
	def initialComment(self):
		#rules for gamers
		#done by AutomMderator
		None
	def check24h(self,id):
		#when no reply after 24h delte the submission
		#set flair locked
		#remove submission
		None
	#####################################
	
	def rebootClass(self,err):
		log.error("FATAL, restart class {}".format(str(err)))	
		os.system("python main.py")	
	
	
	
if __name__ == "__main__":			
	obj = MO()
	db= DBhelper()
	obj.getDatabase(db)
	obj.streamAll()
	


