var finalhandler = require('finalhandler')
var http         = require('http')
var Router      = require('router')
var moment = require('moment');
require('moment-range');
var fs = require('fs')
var jsdom = require('jsdom')
, request = require('request')
, url = require('url')

var router = Router()

var waitTime = 2000 //time in millisecond

function getDateRange(){
    var startdate = moment('2016-01-01');
    var enddate = moment('2013-06-01');
    var enddate = moment(new Date());
    var dates = [];
    for (var m = startdate; m.isBefore(enddate); m.add(1,'days')) {
      dates.push(m.format('YYYYMMDD'));
  }
  return dates;    
}


router.get('/', function (req, res) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Connection', 'Transfer-Encoding');
  res.setHeader('Transfer-Encoding', 'chunked');
  res.write("Scraping nba data...<hr>");
  var dates = getDateRange();
 // console.log(dates);
  getScrapInInterval(dates,res);
  //getGameDetailLinks(date,res);
  //res.end("Done");
})

function getScrapInInterval($dates,res){
  var c = 0;
  var timeout = setInterval(function() {
    getGameDetailLinks($dates[c],res);
    c++;
    if (c > $dates.length) {
      clearInterval(timeout);
    }
  }, waitTime);
}

router.get('/parsedata', function (req, res) {
	fs.readFile('./parser.html', function (err, html) {
        if (err) {
            throw err; 
        } 
        res.writeHeader(200, {"Content-Type": "text/html"});  
        res.write(html);  
        res.end();

    });
})

function getGameDetailLinks($date,res){
    //var $date = "20160107";
    res.write("Getting all games for date "+$date+"...");
    var headers = {'headers': {
      'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
      }
    }

    request({headers,uri:'http://www.nba.com/gameline/'+$date+'/'},function(err, response, body){

        if(err && response.statusCode !== 200){console.log('Request error.');}

        jsdom.env({
            html: body,
            scripts: ['http://code.jquery.com/jquery-1.6.min.js'],
            done: function (err, window) {
                    parseDetailLinks(window,res,$date);
                }
            });
    });  
}

function parseDetailLinks(window,res,$date){
    var $ = window.jQuery;
    $title = $('title');
    if ($title.text().indexOf("Page Not Found") < 0){
        var finallinks = [];
        $body = $('body')
        $links = $body.find('a.recapAnc');
        res.write($links.length+" games found...");
        $links.each(function (i, item) {
            var link = $(item).attr("href");
            link ='http://nba.com'+link;
            finallinks.push(link);
        });
        getData(finallinks,res,$date);
    }
    else{
        res.write("..Games not found for the day.");
        console.log("Data not found for date: "+$date);
    }
    return finallinks; 
}

function getData($urls,res,$date){
    var c = 0;
    var timeout = setInterval(function() {
    getDataForEachGame($urls[c],res,$date);
    c++;
    if (c > $urls.length) {
      clearInterval(timeout);
    }
    }, waitTime);
}
function getDataForEachGame($url,res,$date){
    console.log($url);
    if($url == undefined){
        return;
    }
    //$url = "http://www.nba.com/games/20160104/TORCLE/gameinfo.html";
    $urlparts = $url.split("/");
    $filename = $urlparts[4]+"-"+$urlparts[5];
    res.write("Getting data for the game:"+$filename);
    request({headers: {
      'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    },
    uri: $url}, function(err, response, body){
        var self = this;
        self.items = new Array();//I feel like I want to save my results in an array
        //Just a basic error check
        if(err && response.statusCode !== 200){console.log('Request error.');}

        jsdom.env({
            html: body,
            scripts: ['http://code.jquery.com/jquery-1.6.min.js'],
            done: function (err, window) {
                    res.write("..Data downloaded for the game...");
                    //res.send($('div#nbaGIPBP').text());
                    //res.send($('title').text());
                    //extractDataFromPage(window,res,$date,$filename);
                    extractTableFromPage(window,res,$date,$filename);
                }
            });
    });
}

function extractTableFromPage(window,res,$date,$filename){
    res.write("extracting play by play data...");
    var $ = window.jQuery;
    $body = $('body')
    $table = $body.find('div#nbaGIPBP table')[0].outerHTML;
    $filename = 'htmldata/'+$filename+'.html';
    fs.writeFile($filename,$table, function (err) {
      if (err) return console.log(err);
      res.write("Data written into the file.."+$filename+"...");
      console.log('Data written for file:'+$filename);
      res.write("Done!!!");
      res.write("<hr>");
    });
    
}

function extractDataFromPage(window,res,$date,$filename){
//Use jQuery just as in a regular HTML page
    var dta = [];
    var $ = window.jQuery;
    $body = $('body')
    $tr = $body.find('div#nbaGIPBP table tr');
    $tr.each(function (i, item) {
        var data1 = $(item).text();
            //data1 = data1.replace(/,/g , '').replace(/^\s\s*/, '').replace(/\s\s*$/, '');
            var lines = data1.split(/\n/);
            var newlines = [];
            $.each(lines,function(i,item1){
                newlines.push($.trim(item1));
            });
            newlines = newlines.filter(Boolean)
            
            //lines = lines.filter(Boolean)
            $left = $(item).children('td.nbaGIPbPLft,td.nbaGIPbPLftScore,div.gameEvent');
            $mid = $(item).children('td.nbaGIPbPMid,td.nbaGIPbPMidScore');
            $right = $(item).children('td.nbaGIPbPRgt,td.nbaGIPbPRgtScore');
            dta.push(newlines);
        });
    fs.writeFile('data/'+$filename+'.json',JSON.stringify(dta), function (err) {
      if (err) return console.log(err);
      console.log('Data written for filename:'+$filename);
      res.write("Done!!!");
      res.write("<hr>");
    });
    //console.log(self.items);
    
}

var server = http.createServer(function(req, res) {
  router(req, res, finalhandler(req, res))
})

server.listen(3000)