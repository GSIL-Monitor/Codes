var ports = [],
    datas = [];
chrome.runtime.onConnect.addListener(function(port) {
    if (port.name !== "devtools") return;
    ports.push(port);
    port.onDisconnect.addListener(function() {
        var i = ports.indexOf(port);
        if (i !== -1) ports.splice(i, 1);
    });
});

chrome.runtime.onMessage.addListener(function(msg) {
    if(localStorage['drawOver'] == 1){
        datas = [];
        localStorage['drawOver'] = null;
    }
    datas.push(msg);
    localStorage["domains"] = JSON.stringify(datas);
});