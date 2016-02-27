# import urllib3
import requests
import json
# http = urllib3.PoolManager()
# http.headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
# http.headers['Referer'] = "http://stats.nba.com/scores/"
url = "http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate=10%2F23%2F2015"
s = requests.Session() 
s.headers.update({'Referer': 'http://stats.nba.com/scores/','User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}) 
r = s.get(url)
print(r.status_code)
data_dict = json.loads(r.text)
noofgame = len(data_dict['resultSets'][0]['rowSet'])
date = data_dict['parameters']['GameDate']
gameids = []
for i in range (0,noofgame-1):
	gameid = data_dict['resultSets'][0]['rowSet'][i][2]
	gameids.append(gameid)

print(noofgame)
print(date)
print(gameids)
#print(r.text)