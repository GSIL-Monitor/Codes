
var page = require('webpage').create(),
    system = require('system');
    page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36';

var address;
var id
//function waitFor(timeOutMillis) {
//            var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 3000, //< Default Max Timout is 3s
//            start = new Date().getTime(),
//            interval = setInterval(function() {
//                if ( (new Date().getTime() - start > maxtimeOutMillis)) {
//                    // If timeout
//                    console.log("'waitFor()' timeout");
//                    clearInterval(interval); //< Stop this interval
//                    return
//                }
//                else {
//                    console.log("not complete")
//                }
//            }, 250); //< repeat check every 250ms
//         };

//console.log(system.args.length)
if(system.args.length < 4){
    phantom.exit();
}else{
    address = system.args[1];
    id = system.args[2]
    dest = system.args[3]
    t = Date.now();
    page.viewportSize = { width: 1280, height: 800 };
    page.clipRect = { top: 0, left: 0, width: 1280, height: 800 }
    console.log(address)
    page.open(address, function (status){
        console.log(status)
        if (status != "success"){
            console.log('FAIL to load the address');
            phantom.exit();
        }

        t = Date.now() - t;
        console.log('Loading ' + system.args[1]);
        console.log('Loading time ' + t + ' msec');

        window.setTimeout(function (){
                //在本地生成截图
            page.render(dest+id+".jpg");
            //console.log(page.content);
            page.close()
            phantom.exit();
        }, 2000);

    });
}