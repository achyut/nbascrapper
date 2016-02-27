import urllib3
import json
from time import gmtime, strftime
from threading import Timer

startgame = 21500489
#endgame = 21500822
delay = 5
start = strftime("%Y-%m-%d %H:%M:%S", gmtime())
urls = []
gameidmapper = {}
http = urllib3.PoolManager()
http.headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"

def loadUrls():
	global startgame
	tempgame = startgame
	#while(tempgame>endgame):
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
	startgame = tempgame

def elapsedmin():
	end = time.time()
	elapsed = end - start
	min = elapsed/60
	return str(elapsed)

def download():
	currenttime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	print("")
	print(bcolors.BOLD + bcolors.OKBLUE+"-----------------------------------------------------------------------------------------------"+ bcolors.ENDC)
	print(bcolors.BOLD + bcolors.OKBLUE+"--"+bcolors.ENDC+bcolors.OKGREEN+" Process start time: "+bcolors.WARNING+bcolors.BOLD+str(start)+bcolors.ENDC+bcolors.OKGREEN+"-----current time: "+bcolors.WARNING+bcolors.BOLD+str(currenttime)+bcolors.ENDC+bcolors.OKGREEN+"----"+bcolors.ENDC)
	urlobj = urls.pop()
	gametype = urlobj[0]
	gameid = urlobj[1]
	url = urlobj[2]
	if gametype is 'playbyplay':
		downloadPlayByPlay(gameid,url)
	else:
		downloadBoxScore(gameid,url)

def downloadPlayByPlay(gameid,url):
	print(bcolors.BOLD + bcolors.OKBLUE+"--"+bcolors.ENDC+bcolors.OKGREEN+" Downloading play by play data for gameid"+bcolors.FAIL+bcolors.BOLD+" %s" % gameid+""+bcolors.ENDC)
	response = http.request('GET',url)
	if response.status == 200:
		date = gameidmapper[gameid]
		filename = "playbyplay/"+date+"_"+str(gameid)+".json"
		savedata(response.data,filename)
		gameidmapper.pop(gameid, None)
	else:
		print(bcolors.BOLD + bcolors.OKBLUE+"--"+bcolors.ENDC+bcolors.FAIL+" Response status %s for gameid %s" % response.status,gameid +""+bcolors.ENDC)

def downloadBoxScore(gameid,url):
	print(bcolors.BOLD + bcolors.OKBLUE+"--"+bcolors.ENDC+bcolors.OKGREEN+" Downloading boxscore for gameid"+bcolors.FAIL+bcolors.BOLD+" %s " % gameid+""+bcolors.ENDC)
	response = http.request('GET',url)
	if response.status == 200:
		data_dict = json.loads(response.data.decode('utf8'))
		date = data_dict['resultSets'][0]['rowSet'][0][0]
		gameidmapper[gameid] = date
		filename = "boxscore/"+date+"_"+str(gameid)+".json"
		savedata(response.data,filename)
	else:
		print(bcolors.BOLD + bcolors.OKBLUE+"--"+bcolors.ENDC+bcolors.FAIL+" Response status %s for gameid %s"+filename % response.status,gameid +""+bcolors.ENDC)


def savedata(data,filename):
        file = open(filename, 'wb')
        file.write(data)
        file.close()
        print(bcolors.BOLD + bcolors.OKBLUE+"--"+bcolors.ENDC+bcolors.OKGREEN+" File written sucessfully!!! for filename "+filename+bcolors.ENDC)
        print(bcolors.BOLD + bcolors.OKBLUE+"-----------------------------------------------------------------------------------------------"+bcolors.ENDC)

# function to run scheduler
def runscheduler():
	Timer(delay,runscheduler).start()
	if(len(urls)<=0):
		loadUrls()
	download()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

runscheduler()

