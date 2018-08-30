var request = require('request'),
	fs = require('fs');
var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');
var co = require('co');

var mongo_url = 'mongodb://10.44.176.22:27017/crawler_v2';
//var mongo_url = 'mongodb://192.168.1.202:27017/crawler_v2';
var db;

var url_prefix = 'http://shouji.baidu.com/soft/item?docid=';
var start = 1
var latest = 0
var group=50
var crawled = 0

function startCrawl() {
    for(var i=start;i<start+group;i++) {
        var url = url_prefix + i;
        request({url: url, timeout:30000, idx:i}, processDetail);
    }
}

function processDetail(err, rsp, body) {
    if( !err && rsp.statusCode == 200 ){
        //console.log(rsp.statusCode);
        console.log(rsp.request.uri.href);
        if( body.indexOf("请检查您所输入的URL地址是否有误。") > 0 ){
            console.log("Not exists!")
        }
        else{
            db.collection("market_baidu").findOne({key:rsp.request.idx},{fields:{_id:1},limit:1},
                function(err, result){
                    //console.log(result)
                    if( !result ){
                        db.collection('market_baidu').insertOne({
                            "key":rsp.request.idx,
                            "url":rsp.request.uri.href,
                            "content":body,
                            "date": new Date()
                            },
                            function(err,result){
                                if(err){
                                    console.log("insert error!");
                                }
                        });
                    }
            })

            if(rsp.request.idx > latest){
                latest = rsp.request.idx;
            }
        }
    }
    else{
        console.log("Error!")
    }

    crawled++;
    if(crawled >= group){
        start += group;
        console.log("start=" + start + ", latest=" + latest);
        if( (start < 8000000) || (start < latest + 2000) ){
            crawled = 0
            startCrawl();
        }
        else{
            db.close();
            process.exit();
        }
    }
}

co(function*() {
    console.log("start...");
    db = yield MongoClient.connect(mongo_url);

    var all = false;
    var options = process.argv;
    for(var i=0;i<options.length;i++){
        if(options[i] == "all"){
            all = true;
        }
    }

    latest = 0
    start = 1

    if(all == false){
        var doc = yield db.collection('market_baidu').findOne({},{sort:[['key',-1]],limit:1});
        if(doc != null){
            console.log("start: " + doc["key"]);
            latest = doc["key"]
            start = latest + 1
        }
    }

    startCrawl();
});
