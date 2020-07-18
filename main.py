import praw
from datetime import datetime
import configparser
import logging as log

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
		None
	
	def connectReddit(self):
		_UA = 'MOB by /u/[yourouija]'
		reddit = praw.Reddit("bot1",user_agent=_UA)
		reddit.validate_on_submit=True	
		
		return reddit
	
	def closeGame():
		#setFlair
		#lockThread
		#comment winner comment
		#send message to creator that puzzle has solved
		None
	
	
	def startGame():
		#setFlair
		#unLockThread
		#send message to creator that puzzle has started
		None
	
	
	
	def streamPosts(self):
		reddit = self.connectReddit()
		for submission in reddit.subreddit('MysteryObject').stream.submissions():
			print(submission.selftext)
			print(submission.id)
			print(submission.author.name)
			print(submission.url)
			print(submission.title)
			print(submission.locked)
			
	def sendAuthorWelcomeMessage(self):
		#Done by Automoderator
		None
		
		
		
		
		
		
		
		
		
		
	def StreamRedditStuff(i,redditID,subreddit,_igu):
		reddit = ConnectReddit()
		for comment in reddit.subreddit(subreddit).stream.comments():
		#for comment in reddit.subreddit('TheGamerLounge').stream.comments():

			if comment.parent_id == "t3_"+redditID:

				dt_object = datetime.fromtimestamp(comment.created_utc)
			
				#print("Comment found:\r\nUser: %s \r\nCreated:%s \r\nBody: %s \r\n"%(comment.author.name,dt_object,comment.body))
				
				if comment.author.name not in _igu:
					insertTrigger(*connectDB(),comment.id,comment.created_utc,comment.body.lower(),comment.author.name,comment.parent_id)
					
							
				else:
					print("User ignored: %s" %comment.author.name)
				
				
				if comment.body.lower() == 'scoreboard':
					r = getColorsforGame(*connectDB(),parent_ID="t3_"+redditID)
					#sendscoreboard(True,r,comment.id)
				
			time.sleep(0.05)
			
			
			
a = MO()
a.streamPosts()			
