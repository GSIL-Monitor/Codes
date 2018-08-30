var url = 'http://weixin.sogou.com/weixin?query=%E8%98%91%E8%8F%87%E8%A1%97';
var page = require('webpage').create({
  parameters: {
        proxy: '117.177.250.147:81'
    }
});
page.open(url);
page.onLoadFinished = phantom.exit;
page.onResourceReceived = function(j) {
//  console.log('Running... [' + j.url + ']');

  if (j.url == url){
    console.log(page.content)

    for (var i = 0; i < j.headers.length; i++) {
        console.log(j.headers[i].name + ': ' + j.headers[i].value);
    }

//    cookie = ''
//    for (var i = 10; i < 16; i++) {
//        console.log(j.headers[i].value)
//        cookie =  cookie+ j.headers[i].value;
//    }
//
//    console.log(cookie)

  }
};

page.onResourceRequested = function(req){
	console.log(j.headers)
}