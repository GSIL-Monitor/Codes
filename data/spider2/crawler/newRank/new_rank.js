
var page = require('webpage').create(),
    system = require('system');
    page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36';
//    page.settings.resourceTimeout = 320000

//phantom.addCookie({
//  'name'     : 'tt_webid',   /* required property */
//  'value'    : '6504050983600719373',  /* required property */
//  'domain'   : '.toutiao.com',
//  'expires'  : (new Date()).getTime() + (1000 * 60 * 60)   /* <-- expires in 1 hour */
//});

var address;

//page.onResourceRequested = function(requestData, networkRequest) {
//    console.log('Request (#' + requestData.id + '): ' + JSON.stringify(requestData));
//};
page.onResourceReceived = function(response) {
    console.log('Response (#' + response.id + ', stage "' + response.stage + '"): ' + JSON.stringify(response));
};

//console.log(system.args.length)
if(system.args.length < 1){
    phantom.exit();
}else{
    address = system.args[1];
    t = Date.now();
    console.log(address)
    page.open(address, function (status){
        console.log(status)
        if (status != "success"){
            console.log('FAIL to load the address');
            var cookies = page.cookies;

            console.log('Listing cookies:');
            for(var i in cookies) {
                console.log(cookies[i].name + '=' + cookies[i].value);
            }
            phantom.exit();
        }

        t = Date.now() - t;
        console.log('Loading ' + system.args[1]);
        console.log('Loading time ' + t + ' msec');


// Run a function in the webpage's context and catch what it returns.
        var html = page.evaluate(function() {
            // Optionally, do some more page manipulation here.
            // ...

            // Return the HTML from the loaded and JS-manipulated page.
            // Note that a console.log() here in this context won't be visible (by default).
            // return document.documentElement.outerHTML;

            return document.documentElement.outerHTML

        });

        // Print the HTML to standard output.
        console.log(html);
        var cookies = page.cookies;

        console.log('Listing cookies:');
        for(var i in cookies) {
            console.log(cookies[i].name + '=' + cookies[i].value);
        }

        phantom.exit()
//        window.setTimeout(function (){
//                //在本地生成截图
//            page.render("jpeg/1.jpg");
//            //console.log(page.content);
//            page.close()
//            phantom.exit();
//        }, 2000);
    });
}