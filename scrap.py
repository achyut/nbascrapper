from lxml import html
import requests
page = requests.get('http://www.nba.com/games/20160104/TORCLE/gameinfo.html')
tree = html.fromstring(page.content)
#This will create a list of buyers:
buyers = tree.xpath('//div[@id="nbaGIPBP"]/text()')
#This will create a list of prices
#prices = tree.xpath('//span[@class="item-price"]/text()')
print 'Buyers: ', buyers
#print 'Prices: ', prices

