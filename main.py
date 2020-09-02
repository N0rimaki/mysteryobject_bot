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
import argparse

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
			reddit = praw.Reddit("bot5",user_agent=_UA)
			reddit.validate_on_submit=True	
			self.r = reddit
		except Exception as err:
			log.error("Exception {}".format(str(err)))
			self.rebootClass(err)
				
		self.flair_solved = "882c5aa6-c926-11ea-a888-0e38155ddc41"
		self.flair_running = "7ae507b2-c926-11ea-8bf8-0ef44622e4b7"
		self.flair_onhold = "4aecca10-c99c-11ea-bc5c-0e190f721893"
		self.selfcall = False
		
		log.info("Starting the Bot Class, omg i'm nervous! Starting in sub r/{}".format(self.subredditname))	
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
		#deactivated 26.08.2020
		#submission.mod.lock()
		#add timestamp of solving
		self.getDatabase(db.updateTimestamp_stop(rid))
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

	
	def runSingleSubmission(self,parent_ID):
		submission = self.r.submission(id=parent_ID)
		submission.comment_sort = "old"

		for comment in submission.comments:
			if comment.author.name != 'AutoModerator' and comment.author.name != 'yourouija':
				prettytime = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
				log.info("Run Single Submission SID:{} CID:{} - userguess: {} - created_utc: {}".format(parent_ID,comment.id,comment.body,prettytime))
				self.processCommentMutlipleWords(comment)
		#self.selfcall = False
	
	
	
	def processCommentMutlipleWords(self,comment):
		start_time = time.time()
		start_time = start_time+(24*60*60)
		#Here we analyze the comment and compare user comment with databasesolution
		#parent_ID = comment.parent_id.replace('t3_','')
		parent_ID = comment.submission.id.replace('t3_','')
		
		ss = self.getDatabase(db.getSolutionforID(parent_ID))
		
		userguess = re.sub(r"[^A-Za-z0-9ÄäÖöÜü$€¥£¢₧\!& -]","",comment.body.lower().strip())
		


		if userguess == "!hint":
			try:
				self.getDatabase(db.updateHintcount(parent_ID))
				hinttmp = self.getDatabase(db.getHintcount(parent_ID))[0]
				hintcounter = int(hinttmp[0])
				gamestatus = int(hinttmp[2])				

				log.info("User want hints for {} - counter:{}".format(parent_ID,hintcounter))
				
				if hintcounter >= 5 and gamestatus != 2:#and if comment.created_utc > start_time

					log.info("User becomes hint for {}".format(ss))
					self.postHint(parent_ID,ss)
					self.getDatabase(db.updateStatus(parent_ID,"2"))
			except Exception as err:
				log.error("hintcounter {}".format(str(err)))	
	
		elif userguess == "!rescanoff" and self.selfcall == False:

			log.info("User {} want rescan for {}".format(comment.author.name,parent_ID))			
			self.runSingleSubmission(parent_ID)	
			#self.selfcall = True
			comment.reply("_sigh_ okidoki, maybe i forgot to scan some comment. i will do a rescan now.")	
		
		elif userguess == "!import" and comment.author.name == "wontfixit":

			log.info("submission {} reimport".format(parent_ID))			
			#here we monitor for new submissions
			self.getDatabase(db.addNewGame(comment.submission))	
			#self.initialComment(submission.id)
			self.updateUserFlair(comment.submission.author.name)
			comment.reply("_sigh_")	
		
		else:
			for s in ss:
				solution = str(s[0])
				tmpsolution = solution.lower()
				
				try:
					tmpsolution = ast.literal_eval(tmpsolution)
					tmpsolution = [n.strip() for n in tmpsolution]
				except Exception as err:
					log.error("string to list: {}".format(str(err)))			
				

				self.getRuntime(parent_ID)
				prettytime = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
				log.info("User: {} at {} try \"{}\" = {} on \"{}/{}\"".format(comment.author.name,prettytime,userguess,tmpsolution,parent_ID,comment.submission.title))

				#for solutionword in tmpsolution:
				checktuple = self.checkSolution(userguess,tmpsolution)
				if checktuple != None:
					if ___runprod___ == True:
						self.closeGame(parent_ID,1)						
						self.madeWinnerComment(comment,parent_ID,tmpsolution)

						self.getDatabase(db.updateStatus(parent_ID,1))
						self.getDatabase(db.addWinner(comment.author.name,comment.permalink,comment.submission.title))
						self.updateUserFlair(comment.author.name)
						self.updateLeaderboard()
					else:
						log.info("RUN only in DEMO mode, no changes were made at the submission.")
					
					
					log.info("Solution found: {} {} \"{}/{}\" \"{}\" in {} -body \"{}\"".format(comment.author.name,comment.id,parent_ID,comment.submission.title,str(checktuple[1]),str(tmpsolution),str(userguess)))
	
	def checkSolution(self,userguess,solution):
		#check if the guess of the user is includet in the solution
		#this works very well
		for words in solution:
			if re.search(r'\b' + words + r'\b', userguess):
				return bool(words),words
		
		
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
	
	
	def postHint(self,parent_ID,solution):
		#regex = re.compile(r"(?<!^)[^\s](?!$)")
		regex = re.compile(r"(?<!^)[^\s\"]")
		tmpStarString=""
		for s in solution:
			solution = str(s[0])
			tmpsolution = solution.lower()
			
			try:
				tmpsolution = ast.literal_eval(tmpsolution)
				tmpsolution = [n.strip() for n in tmpsolution]
			except Exception as err:
				log.error("string to list: {}".format(str(err)))	
				
			for words in tmpsolution:
				words = words.replace(" ","\"")
				tmp = re.sub(regex,' \_ ',words)
				tmpStarString += tmp+ ", "
			
			#log.info("--->{}".format(tmpStarString))	
		
		submission = self.r.submission(id=parent_ID)
		modcommentid = submission.reply("Hint: >!"+str(tmpStarString)+"!<")
		#made mod comment sticky 
		comment = self.r.comment(modcommentid)
		comment.mod.distinguish(how="yes", sticky=True)		
		log.info("Bot made hint comment {}".format(parent_ID))	
		None
	
	def getRuntime(self,parent_ID):
		timestamps = self.getDatabase(db.getTimestamps(parent_ID))

		for ts in timestamps:
			timestamp_start = int(ts[0])
			timestamp_stop = int(ts[1])
#		runtime = timestamp_stop-timestamp_start

		d = divmod(timestamp_stop-timestamp_start,86400)  # days
		h = divmod(d[1],3600)  # hours
		m = divmod(h[1],60)  # minutes
		s = m[1]  # seconds
		
		log.info("{}d {}h {}m {}s ".format(d[0],h[0],m[0],s))	
	#	print '%d days, %d hours, %d minutes, %d seconds' % (d[0],h[0],m[0],s)
		return "{}d {}h {}m {}s ".format(d[0],h[0],m[0],s)
	
	
	def madeWinnerComment(self,comment,parent_ID,solution):
		runtimetext = self.getRuntime(parent_ID)

		sol = ""
		i = len(solution)
		j=1
		for w in solution:
			
			if j == i:
				sol += w
			else:
				sol += w+", "
			j += 1

		#reply that user have won
		comment.reply("you win this round, go and make a new post for us. :) ")
		user = comment.author.name
		#made mod submission with winner
		submission = self.r.submission(id=parent_ID)
		modcommentid = submission.reply("I AM THE LAW - User u/"+user+" has won the round.\n\rOPs solutions: * "+str(sol)+" *\n\rY'all took "+runtimetext+" to solve it")
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
					if comment.author.name != 'AutoModerator' and comment.author.name != 'yourouija':	
						#if some comment is found, it enter here the processing of the comment
						self.processCommentMutlipleWords(comment)
					
				for submission in submission_stream:
					if submission is None:
						break
					if submission.created_utc < start_time:
						continue
					#regex for only do some action when picture submission is detected, i bet there is some better methode	
					regex = r"https:\/\/i\.redd\.it|https:\/\/i\.imgur\.com|https:\/\/v\.redd\.it|https:\/\/imgur\.com"
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
		os.system("python3 /home/pi/mysteryobject_bot/main.py")	
	
	
	
if __name__ == "__main__":			
	
	ap = argparse.ArgumentParser(description="Post the submission ID")
	ap.add_argument("-s" ,dest='SubmissionID',type=str, required=False,
		help="Submission ID only xxx.py -s h4No0B")
	argument = ap.parse_args()

	if argument.SubmissionID != None:
		log.info("Single Submission processed SID:{}".format(argument.SubmissionID))
		singleobj = MO()
		db = DBhelper()
		singleobj.getDatabase(db)
		singleobj.runSingleSubmission(argument.SubmissionID)
		exit()
	elif argument.SubmissionID == None:
		log.info("Class started regular ")
		obj = MO()
		db = DBhelper()
		obj.getDatabase(db)
		obj.streamAll()
		log.info("no arg {}".format(argument.SubmissionID))
		None













