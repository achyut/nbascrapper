import os
import requests
import json
from time import gmtime, strftime
from threading import Timer
import datetime
import notify

DELAY = 5

#format should be m-d-yyyy

startdate = "1-12-1971"

ERROR_CHECK_INTERVAL = 10
MAX_RETRIES = 5
MAX_DIFF_SECONDS = 120

lastwritten = datetime.datetime.now()
start = strftime("%Y-%m-%d %H:%M:%S", gmtime())
urls = []
gameidmapper = {}
errorcount = 1
#http = urllib3.PoolManager()
#http.headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
session = requests.Session() 
session.headers.update({'Referer': 'http://stats.nba.com/scores/','User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}) 

def getnextdate():
	global startdate
	start = datetime.datetime.strptime(startdate, "%m-%d-%Y")
	nextdate = start + datetime.timedelta(days=1)
	if nextdate > datetime.datetime.now():
		print("Completed the downloading process. Bye Bye!!")
		os._exit(0)

	nextdatestr = nextdate.strftime("%m-%d-%Y")
	startdate = nextdatestr
	return nextdate

def getGameIds():
	localdate = getnextdate()
	month = localdate.month
	day = localdate.day
	year = localdate.year
	url = "http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate="+str(month)+"%2F"+str(day)+"%2F"+str(year)
	response = session.get(url)
	gameids = []
	if response.status_code == 200:
		print("-----------------------------------------------------------------------------------------------")
		data_dict = json.loads(response.text)
		noofgame = len(data_dict['resultSets'][0]['rowSet'])
		date = data_dict['parameters']['GameDate']
		print("-- "+str(noofgame)+" found for the date: "+str(date))
		filename = "daydata/"+str(year)+"_"+str(month)+"_"+str(day)+".json"
		savedata(response.text,filename)
		if noofgame > 0 :
			dateobj = datetime.datetime.strptime(date, "%m/%d/%Y")
			datestr = dateobj.strftime("%Y-%m-%d")
			for i in range (0,noofgame-1):
				gameid = data_dict['resultSets'][0]['rowSet'][i][2]
				gameidmapper[gameid] = datestr
				gameids.append(gameid)
			
		else:
			getnextdate()
	else:
		print("-- Response status %s for date %s" % response.status,date +"")
	return gameids
	
	
def loadUrls():
	gameids = getGameIds()
	for gameid in gameids:
		playbyplay = 'http://stats.nba.com/stats/playbyplayv2?EndPeriod=10&GameID=%s&StartPeriod=1&StartRange=0' % gameid
		boxscore = 'http://stats.nba.com/stats/boxscoresummaryv2?GameID=%s' % gameid
		obj = []
		obj.append('playbyplay')
		obj.append(gameid)
		obj.append(playbyplay)
		urls.append(obj)
		obj = []
		obj.append('boxscore')
		obj.append(gameid)
		obj.append(boxscore)
		urls.append(obj)
		
def elapsedmin():
	end = time.time()
	elapsed = end - start
	min = elapsed/60
	return str(elapsed)

def download():
	if(len(urls)<=0):
		gameidmapper.clear()
		loadUrls()
	else:
		currenttime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		print("")
		print("-----------------------------------------------------------------------------------------------")
		print("-- Process start time: "+str(start)+"-----current time: "+str(currenttime)+"----")
		urlobj = urls.pop()
		gametype = urlobj[0]
		gameid = urlobj[1]
		url = urlobj[2]
		if gametype is 'playbyplay':
			downloadPlayByPlay(gameid,url)
		else:
			downloadBoxScore(gameid,url)

def downloadPlayByPlay(gameid,url):
	if gameid in gameidmapper:
		print("-- Downloading play by play data for gameid %s" % gameid+"")
		response = session.get(url)
	
		#response = http.request('GET',url)
		if response.status_code == 200:
			date = gameidmapper[gameid]
			filename = "playbyplay/"+date+"_"+str(gameid)+".json"
			savedata(response.text,filename)
		else:
			print("-- Response status %s for gameid %s" % response.status,gameid +"")
			download()

def downloadBoxScore(gameid,url):
	print("-- Downloading boxscore for gameid %s " % gameid+"")
	#response = http.request('GET',url)
	response = session.get(url)
	
	if response.status_code == 200:
		# data_dict = json.loads(response.text.decode('utf8'))
		# date = data_dict['resultSets'][0]['rowSet'][0][0]
		# gameidmapper[gameid] = date
		date = gameidmapper[gameid]
		filename = "boxscore/"+date+"_"+str(gameid)+".json"
		savedata(response.text,filename)
		return True
	else:
		print("-- Response status "+str(response.status_code)+" for gameid "+gameid)
		print("-----------------------------------------------------------------------------------------------")
		download()
		return False

def savedata(data,filename):
        file = open(filename, 'w')
        file.write(data)
        file.close()
        print("-- File written sucessfully!!! for filename "+filename)
        print("-----------------------------------------------------------------------------------------------")
        global lastwritten
        lastwritten = datetime.datetime.now()

# function to run scheduler
def runscheduler():
	Timer(DELAY,runscheduler).start()
	download()

def runerrorchecker():
	global ERROR_CHECK_INTERVAL
	ERROR_CHECK_INTERVAL = ERROR_CHECK_INTERVAL * errorcount
	Timer(ERROR_CHECK_INTERVAL,runerrorchecker).start()
	if(errorcount > MAX_RETRIES):
		print("Exiting due to not downloading data from long time!!")
		os._exit(0)
	checkerror()

def checkerror():
	global errorcount
	prev = lastwritten
	now = datetime.datetime.now()
	minDiff = (now-prev)
	if minDiff.seconds > MAX_DIFF_SECONDS:
		errorcount = errorcount + 1
		print("-- Notification message sent.")
		notify.notify_message("No download hapenning from last "+str(minDiff.seconds/60.0)+" minutes. please check into the server. Last downloaded game was from date: "+str(startdate)+" at: "+str(lastwritten))		
		print("-- Error checking in "+str(ERROR_CHECK_INTERVAL)+" seconds.")
if __name__ == '__main__':
	runscheduler()
	runerrorchecker()