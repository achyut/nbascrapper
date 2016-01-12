var finalhandler    = require('finalhandler')
var http            = require('http')
var Router          = require('router')
var moment          = require('moment');
var range           = require('moment-range');
var fs              = require('fs');
var jsdom           = require('jsdom');
var request         = require('request');
var url             = require('url');

var router = Router()

var waitTime = 7000 //time in millisecond

var dates = getDateRange();

var queue = [];
var totalGames = 0;


router.get('/', function (req, res) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Connection', 'Transfer-Encoding');
  res.setHeader('Transfer-Encoding', 'chunked');
  getNextData(res,"");
})

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

function getDateRange(){
    var startdate = moment('2016-01-01');
   // var enddate = moment('2016-01-07');
    var enddate = moment(new Date());
    var dates = [];
    for (var m = startdate; m.isBefore(enddate); m.add(1,'days')) {
      dates.push(m.format('YYYYMMDD'));
  }
  return dates;    
}

function getGameLinks($date,res){
    //var $date = "20160107";
    res.write("<hr>Requesting games for date "+$date+"...");
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
        $body = $('body')
        $links = $body.find('a.recapAnc');
        res.write($links.length+" games found...");
        $links.each(function (i, item) {
            var link = $(item).attr("href");
            link ='http://nba.com'+link;
            queue.push(link);
            totalGames++;
        });   
    }
    else{
        res.write("..Games not found for the day.");
        console.log("Data not found for date: "+$date);
    } 
}

function getNextData(res,$date){
    var timeout = setInterval(function() {
      if(queue.length>0){
        getDataForEachGame(queue.shift(),res,$date);  
      }
      else{
        if(dates.length>0){
          getGameLinks(dates.shift(),res);  
        }
        else{
            clearInterval(timeout);
            res.end("<hr>"+totalGames+" Games data downloaded...Done with scrapping!!!");
        }
      }
      
    }, waitTime);
}

function getDataForEachGame($url,res,$date){
    if($url == undefined){
        return;
    }
    //$url = "http://www.nba.com/games/20160104/TORCLE/gameinfo.html";
    $urlparts = $url.split("/");
    $filename = $urlparts[4]+"-"+$urlparts[5];
    res.write("<br>Requesting data for the game:"+$filename);
    request({headers: {
      'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    },
    uri: $url}, function(err, response, body){
        var self = this;
        self.items = new Array();
        if(err && response.statusCode !== 200){console.log('Request error.');}

        jsdom.env({
            html: body,
            scripts: ['http://code.jquery.com/jquery-1.6.min.js'],
            done: function (err, window) {
                    res.write("...Data downloaded for the game...");
                    extractTableFromPage(window,res,$date,$filename);
                }
            });
    });
}

function extractTableFromPage(window,res,$date,$filename){
    res.write("extracting play by play data...");
    var $ = window.jQuery;
    $body = $('body');
    if($body.find('div#nbaGIPBP table')[0]!==undefined){
      $table = $body.find('div#nbaGIPBP table')[0].outerHTML;
      $filename = 'htmldata/'+$filename+'.html';
      fs.writeFile($filename,$table, function (err) {
        if (err) return console.log(err);
        res.write("Data written into the file.."+$filename+"...");
        console.log('Data written for file:'+$filename);
        res.write("Done!!!");
        //res.write("<hr>");
        //getNextData(res,$date);
      }); 
    }
    else{
        totalGames--;
        res.write("Data not found for the day.");
    }
       
}

function extractDataFromPage(window,res,$date,$filename){
    var dta = [];
    var $ = window.jQuery;
    $body = $('body')
    if($body.find('div#nbaGIPBP table')[0]!==undefined){
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
    }
    else{
      totalGames--;
      res.write("Data not found for the day."); 
    }
}

var server = http.createServer(function(req, res) {
  router(req, res, finalhandler(req, res))
})

server.listen(3000)