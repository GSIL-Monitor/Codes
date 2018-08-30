var { ToggleButton } = require('sdk/ui/button/toggle');
var panels = require("sdk/panel");
var self = require("sdk/self");
var buttons = require('sdk/ui/button/action');
var tabs = require("sdk/tabs");
var prefsvc = require("sdk/preferences/service");
var Request = require("sdk/request").Request;
var notifications = require("sdk/notifications");
var { setInterval } = require("sdk/timers");

var button = ToggleButton({
  id: "tshbao-proxy",
  label: "tshbao proxy",
  icon: {
    "16": "./icon-16.png",
    "32": "./icon-32.png",
    "64": "./icon-64.png"
  },
  onChange: handleChange
});

var myScript = "window.addEventListener('click', function(event) {" +
               "  var t = event.target;" +
               "  if (t.nodeName == 'A')" +
               "    self.port.emit('click-link', t.toString());" +
               "  event.preventDefault();" +
               "}, false);"

var panel = panels.Panel({
  contentURL: self.data.url("panel.html"),
  contentScript: myScript,
  onHide: handleHide
});

panel.port.on("click-link", function(url) {
    //console.log(url);
    if( url == "resource://tshbao/data/next" ) {
        //console.log("get");
        if(current_tab != null){
            current_tab.close();
        }
        handleNext();
    }
    else if( url == "resource://tshbao/data/success" ){
        //console.log("success");
        if(current_tab != null) {
            if(proxy_used != null){
                prefsvc.set("network.proxy.type",0);
                var ip_port = proxy_used["ip:port"].split(":")
                var http_type = proxy_used["http_type"]
                Request({
                    url: "http://www.xiniudata.com/api/admin/proxy/tyc/add",
                    contentType:"application/json",
                    content:JSON.stringify({"ip":ip_port[0], "port":parseInt(ip_port[1]),"type":http_type}),
                    onComplete: function (response) {
                        proxy_success++;
                        notifications.notify({
                            text: "success: " + proxy_success,
                        });
                    }
                }).post();
            }
            current_tab.close();
        }
    }
    else if( url == "resource://tshbao/data/refresh" ){
        handleRefresh();
    }
    else if( url == "resource://tshbao/data/clean" ){
        prefsvc.set("network.proxy.type",0);
    }
});

function handleChange(state) {
  if (state.checked) {
    panel.show({
      position: button
    });
  }
}

function handleHide() {
  button.state('window', {checked: false});
}


var proxies = [];
var proxy_current = 0;
var proxy_used = null;
var current_tab = null;
var proxy_success = 0;

function openSite(proxy) {
    proxy_used = proxy
    var ip_port = proxy["ip:port"].split(":")
    var http_type = proxy["http_type"]
    prefsvc.set("network.proxy.type",1);
    prefsvc.set("network.proxy.socks",ip_port[0]);
    prefsvc.set("network.proxy.socks_port",parseInt(ip_port[1]));
    if( http_type == "Socks4"){
        prefsvc.set("network.proxy.socks_version",4);
    }
    else{
        prefsvc.set("network.proxy.socks_version",5);
    }
    tabs.open({ 
            //url:"http://www.tianyancha.com/company/2310299181",
            url:"http://antirobot.tianyancha.com/captcha/verify?return_url=http://www.tianyancha.com/company/2310299181",
            onOpen: function onOpen(tab) {
                console.log("open");
                current_tab = tab
            },
            onClose: function onClose(tab) {
                console.log("close");
            },

    });
}

function handleRefresh() {
    prefsvc.set("network.proxy.type",0);
    Request({
        url: "http://proxy.mimvp.com/api/fetch.php?orderid=860150908143212810&num=100&country_group=1&http_type=4,5&result_fields=1,2&result_format=json",
        onComplete: function (response) {
            proxies = response.json["result"];
            proxy_current = 0 ;
            proxy_success = 0;
            notifications.notify({
                text: "refresh: " + proxies.length,
            });
        }
    }).get();
}

function handleNext() {
    prefsvc.set("network.proxy.type",0);
    console.info(proxy_current)
    if( proxies.length == 0 || proxies.length == proxy_current){
        notifications.notify({
            text: "Refresh First!",
        });
    }
    else{
        openSite(proxies[proxy_current]);
        proxy_current++;
        notifications.notify({
            text: "" + proxy_current + "/" + proxies.length,
        });
    }
}

setInterval(function() {
    Request({
        url: "http://www.xiniudata.com/api/admin/proxy/tyc/count",
        onComplete: function (response) {
            count = response.json["count"];
            if( count <= 0 ){
                notifications.notify({
                    text: "No Proxy Now!!!",
                });
            }
        }
    }).get();
}, 60*1000)