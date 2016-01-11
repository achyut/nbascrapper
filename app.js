var finalhandler = require('finalhandler')
var http         = require('http')
var Router      = require('router')
var fs = require('fs')
var jsdom = require('jsdom')
, request = require('request')
, url = require('url')

var router = Router()
router.get('/', function (req, res) {
  res.setHeader('Content-Type', 'text/plain; charset=utf-8')
  res.end('Hello World!')
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

router.get('/getdata', function (req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  //Tell the request that we want to fetch youtube.com, send the results to a callback function
        request({uri: 'http://www.nba.com/games/20160104/TORCLE/gameinfo.html'}, function(err, response, body){
                var self = this;
        self.items = new Array();//I feel like I want to save my results in an array
         
        //Just a basic error check
                if(err && response.statusCode !== 200){console.log('Request error.');}
                //Send the body param as the HTML code we will parse in jsdom
        //also tell jsdom to attach jQuery in the scripts and loaded from jQuery.com

        jsdom.env({
                html: body,
                scripts: ['http://code.jquery.com/jquery-1.6.min.js'],
                done: function (err, window) {
                    //Use jQuery just as in a regular HTML page
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

                            //console.log(obj);
                            //self.items1[i] = obj;
                            self.items[i] = newlines

                       });
                        
                     //console.log(self.items);
                    res.end(JSON.stringify(self.items));
                    //res.send($('div#nbaGIPBP').text());
                    //res.send($('title').text());
                }
            });
      
        });
})
 

var server = http.createServer(function(req, res) {
  router(req, res, finalhandler(req, res))
})
 
server.listen(3000)