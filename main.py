import praw
from datetime import datetime
import configparser
import logging as log
from DBhelper import *

now = datetime.now()
timestamp = datetime.timestamp(now)
timeMinusOneDay = timestamp-(24*60*60)



#LOG_FILENAME = "/home/pi/mysteryobject_bot/log_MObot.txt"
LOG_FILENAME = "./log_MObot.log"


___debug___ = True
___runprod___= False

if ___debug___ == True:
	log.basicConfig(filename=LOG_FILENAME,level=log.INFO,format='%(message)s')



class MO:
	
	def __init__(self):
		# config = configparser.ConfigParser()
		# config.read('/home/pi/crosspostbot/config.ini')
		
		# _reddituser = config['DEFAULT']['_reddituser']
		# _subtocrosspost = config['DEFAULT']['_subtocrosspost']
		# _triggerwords =config['DEFAULT']['_triggerwords']
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
		
		
		
	def closeGame(self,rid,reason):
		submission = self.r.submission(id=rid)
		#setFlair
		if reason == 1:
			submission.flair.select(self.flair_solved)
		elif reason == 2:
			submission.flair.select(self.flair_onhold)
				
		#LockThread
		submission.mod.lock()
	
		#comment winner comment
		#send message to creator that puzzle has solved
		None
	
	
	def startGame(self,rid):
		submission = self.r.submission(id=rid)
		#setFlair
		submission.flair.select(self.flair_running)
		#unLockThread
		submission.mod.unlock()
		#send message to creator that puzzle has started?
		
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
		
			if solution in comment.body:
				
				self.madeWinnerComment(comment,parent_ID)
				self.closeGame(parent_ID,1)
				self.getDatabase(db.updateStatus(parent_ID,1))
				self.getDatabase(db.addWinner(comment.author.name,comment.submission.url,comment.submission.title))
				self.updateUserFlair(comment.author.name)
				
				return "Solution found: "+solution
	
	
	def updateUserFlair(self,authorname):
		#count how many puzzles the person solved
			#update the flair Solved:xx
		result = self.getDatabase(db.getSolvedbyUser(authorname))
		for r in result:
			flairtext="solved:"+str(r[0])
		
		self.r.subreddit(self.subredditname).flair.set(authorname, flairtext)
		None
	
	def madeWinnerComment(self,comment,parent_ID):
		#reply that user have won
		comment.reply("you win this round")
		#made mod submission with winner
		submission = self.r.submission(id=parent_ID)
		modcommentid = submission.reply("IAM THE LAW - Add here who has won the round")
		#made mod comment sticky 
		comment = self.r.comment(modcommentid)
		comment.mod.distinguish(how="yes", sticky=True)		
		None
		
	def getMessages(self):
		#Read Messages 
		#safe Title in DB
		#anser if not readable
		None
	
	def sendMessageNoSolution(self):
		#i cant read your solution, seems there is some issue with formating
		#try again
		None
		
	def sendMessageSuccesfullSolved(self):
		#Your puzzle ID has solved by 
		#wontdothis
		None
		
	
	def sendAuthorWelcomeMessage(self):
		#Done by Automoderator
		None
		
	def hint(self):
		#upvote this comment to get a hint
		#10 updoots post first and last letter X......xrange
		None
		
	def streamAll(self):
		#reddit = self.connectReddit()
		
		comment_stream = self.r.subreddit(self.subredditname).stream.comments(pause_after=-1)
		submission_stream = self.r.subreddit(self.subredditname).stream.submissions(pause_after=-1)
		while True:
			try:
				for comment in comment_stream:
					if comment is None:
						break
					#print(comment.author.name)
					#print(comment.body)
					k = self.processComment(comment)
					
				for submission in submission_stream:
					if submission is None:
						break
					#print(submission.title)
					self.getDatabase(db.addNewGame(submission))
			

			except Exception as err:
				print(str(err))
		
		
		
		
	
			
			
			
a = MO()
db= DBhelper()
a.getDatabase(db)

#a.startGame("hveod8")	
#a.closeGame("hveod8",2)		
a.streamAll()
	


