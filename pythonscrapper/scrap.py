import urllib3
import json
from time import gmtime, strftime
from threading import Timer

startgame = 21500830
#startgame = 29900424
endgame = 21500822
delay = 5
start = strftime("%Y-%m-%d %H:%M:%S", gmtime())
urls = []
gameidmapper = {}
http = urllib3.PoolManager()
http.headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
def loadUrls():
	tempgame = startgame
	while(tempgame>endgame):
		gameid = '00'+str(tempgame)
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
		#urls.append({'boxscore':boxscore})
		tempgame = tempgame - 1

def elapsedmin():
	end = time.time()
	elapsed = end - start
	min = elapsed/60
	return str(elapsed)

def download():
	currenttime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	print("")
	print("-----------------------------------------------------------------------------------------------")
	print("-- Process start time: "+str(start)+"--current time: "+str(currenttime)+"----")
	urlobj = urls.pop()
	gametype = urlobj[0]
	gameid = urlobj[1]
	url = urlobj[2]
	if gametype is 'playbyplay':
		downloadPlayByPlay(gameid,url)
	else:
		downloadBoxScore(gameid,url)

def downloadPlayByPlay(gameid,url):
	print("-- Downloading play by play data for gameid %s" % gameid)
	response = http.request('GET',url)
	if response.status == 200:
		date = gameidmapper[gameid]
		filename = "playbyplay/"+date+"_"+str(gameid)+".json"
		savedata(response.data,filename)
		gameidmapper.pop(gameid, None)
	else:
		print("-- Response status %s for gameid %s" % response.status,gameid )

def downloadBoxScore(gameid,url):
	print("-- Downloading boxscore for gameid %s " % gameid)
	response = http.request('GET',url)
	if response.status == 200:
		data_dict = json.loads(response.data.decode('utf8'))
		date = data_dict['resultSets'][0]['rowSet'][0][0]
		gameidmapper[gameid] = date
		filename = "boxscore/"+date+"_"+str(gameid)+".json"
		savedata(response.data,filename)
	else:
		print("-- Response status %s for gameid %s" % response.status,gameid )


def savedata(data,filename):
        file = open(filename, 'wb')
        file.write(data)
        file.close()
        print("-- File written sucessfully!!! for filename "+filename)
        print("-----------------------------------------------------------------------------------------------")

# function to run scheduler
def runscheduler():
	Timer(delay,runscheduler).start()
	if(len(urls)>0):
		download()
	else:
		exit()

loadUrls()
runscheduler()

