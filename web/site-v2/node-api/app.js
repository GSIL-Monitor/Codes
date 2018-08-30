var logger = require('koa-logger');
var route = require('koa-route');
var koa = require('koa');
var app = koa();
var Promise = require('bluebird');
Promise.promisifyAll(require("mongodb"));

app.use(logger());

// route
app.use(route.get('/', home));
app.use(route.get('/news', get));

function *home() {
    this.body = "home"
}

var MongoClient = require('mongodb').MongoClient;
var url = 'mongodb://192.168.1.202:27017/crawler_v2';


function *get() {
    var res = yield 
    MongoClient.connect(url, function(err, db) {
        var collection = db.collection('company');
        collection.find({}).limit(1).toArray(function(err, docs){
            console.log(res);
            console.log(this);
            this.body = docs;
            db.close();
        })
    });
    this.body = res;
}


// listen
app.listen(3000);
console.log('listening on port 3000');