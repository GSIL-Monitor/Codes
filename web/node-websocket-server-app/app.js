var mysql   = require('mysql');
var kafka = require('kafka-node');
var WebSocketServer = require('ws').Server
  , wss = new WebSocketServer({port: 5004});
var config = require("./config");

var register_user = {};

function register(msg, ws) {
    var token = msg["token"];
    if(!!token){
        var connection = mysql.createConnection(config.mysql_config);
        connection.connect();
        connection.query("select * from user_token where token=?", token, function(err,result){
            var flag = false;
            if(err){
                console.log(err);
            }
            else{
                // console.log(result);
                if(result.length==1){
                    var userToken = result[0];
                    var userId = userToken.userId;

                    if(!register_user[userId]){
                        register_user[userId] = [];
                    }
                    register_user[userId].push({
                            "ws":ws,
                            "createTime": (new Date()).getTime()/1000
                        }
                    );
                    flag = true;
                    //console.log(register_user);
                    var data = {"type":"register", "message":"success"};
                    var msg = JSON.stringify(data);
                    ws.send(msg, function ack(error){});
                }
            }
            if(flag == false){
                console.log("Register Fail!");
                var data = {"type":"register", "message":"fail"};
                var msg = JSON.stringify(data);
                ws.send(msg, function ack(error){});
                ws.close(4000);
            }
        })
        connection.end();
    }
    else{
        console.log("Register Fail!");
        var data = {"type":"register", "message":"fail"};
        var msg = JSON.stringify(data);
        ws.send(msg, function ack(error){});
        ws.close(4000);
    }
}

wss.on('connection', function(ws) {
    ws.on('message', function(message) {
        console.log('received: %s', message);
        var msg = JSON.parse(message)
        if(msg.type == "register"){
            register(msg, ws);
        }
    });

    ws.on('close', function(){
        console.log("close");
        for( var key in register_user){
            var items = register_user[key];
            for( var index in items){
                //console.log("index: %s", index);
                //console.log(items);
                if(items[index]["ws"]==ws){
                    items.splice(index,1);
                    break;
                }
                else{
                    var createTime = items[index]["createTime"];
                    var now = (new Date()).getTime()/1000;
                    if( now > createTime + 86400*3 ){
                        items.splice(index,1);
                        break;
                    }
                }
            }
        }
        // console.log(register_user)
    });

    var data = {"type":"connection", "message":"welcome"};
    var msg = JSON.stringify(data);
    ws.send(msg, function ack(error){});
});

var HighLevelConsumer = kafka.HighLevelConsumer;
var Offset = kafka.Offset;
var Client = kafka.Client;
var topic = "websocket_app";
var clientId = 'consumer'+process.pid;
//console.log("clientId: %s", clientId)
var client = new Client(config.kafka_url, clientId);
var payloads = [ { topic: topic }];
var options = {
    groupId: 'node-websocket-server-app',
    id: "worker-" + Math.floor(Math.random() * 10000),
    // Auto commit config
    autoCommit: true,
    autoCommitIntervalMs: 5000,
    // The max wait time is the maximum amount of time in milliseconds to block waiting if insufficient data is available at the time the request is issued, default 100ms
    fetchMaxWaitMs: 100,
    // This is the minimum number of bytes of messages that must be available to give a response, default 1 byte
    fetchMinBytes: 1,
    // The maximum bytes to include in the message set for this partition. This helps bound the size of the response.
    fetchMaxBytes: 1024 * 1024,
    // If set true, consumer will fetch message from the given offset in the payloads
    fromOffset: false,
    // If set to 'buffer', values will be returned as raw buffer objects.
    encoding: 'utf8'
};
var consumer = new HighLevelConsumer(client, payloads, options);
var offset = new Offset(client);

consumer.on('message', function (message) {
    console.log(this.id, message);
    var msg = JSON.parse(message.value);
    var userId= msg.userId;
    if(!!register_user[userId+""]){
        console.log(this.id, "send to userId " + userId);
        var items = register_user[userId+""];
        for(var i in items){
            var ws = items[i]["ws"];
            //console.log(ws);
            ws.send(message.value, function ack(error){
                if(!!error){
                    console.log(error)
                }
            });
        }
    }
    else{
        // console.log(this.id, "can't find ws for userId "+userId)
    }

});
consumer.on('error', function (err) {
    console.log('error', err);
});
consumer.on('offsetOutOfRange', function (topic) {
    console.log("------------- offsetOutOfRange ------------");
    topic.maxNum = 2;
    offset.fetch([topic], function (err, offsets) {
        var min = Math.min.apply(null, offsets[topic.topic][topic.partition]);
        consumer.setOffset(topic.topic, topic.partition, min);
    });
});

var exit =  function () {
    consumer.close(true, function () {
        process.exit();
    });
};

process.on('SIGINT', exit);
process.on('exit', exit);
process.on('uncaughtException', exit);
console.log("Start.")