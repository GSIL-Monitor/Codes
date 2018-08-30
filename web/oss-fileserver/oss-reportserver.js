var http = require("http");
var url = require("url");
var co = require('co');
var OSS = require('ali-oss');

var client = new OSS({
  endpoint: 'http://oss-cn-beijing-internal.aliyuncs.com',
  //endpoint: 'http://oss-cn-beijing.aliyuncs.com',
  accessKeyId: 'LTAIsmDxJhXmRChk',
  accessKeySecret: 'BS3vkDT68fBqdygmhVWeApq8X3sn5x',
  bucket: 'xiniudata-report'
});

http.createServer(function(request, response) {
    var etag = request.headers["if-none-match"];
    var if_modified_since = request.headers['if-modified-since'];
    var file_id = url.parse(request.url).pathname;
    file_id = file_id.match("^/([^/]*)")[1]

    if( file_id == "favicon.ico" ){
        response.writeHead(404, {"Content-Type": "text/plain"});
        response.end();
        return;
    }
    console.log("file_id: " + file_id);
    co(function* () {
        var result = yield client.getStream(file_id);
        //console.log(result);
        var headers = {
            'ETag': result.res.headers["etag"],
            'Cache-Control': 'public, max-age=31536000',
            'Last-Modified': result.res.headers["last-modified"],
            'Expires': "Fri, 01 Jan 2038 01:01:01 UTC",
            'Content-Type': result.res.headers["content-type"],
            'Content-Length': result.res.headers["content-length"]
        };
        if ((etag && etag == result.res.headers["etag"])||(if_modified_since && if_modified_since == result.res.headers["last-modified"])) {
            response.writeHead(304, headers );
            response.end();
            return;
        }
        response.writeHead(200, headers);
        result.stream.pipe(response);
    }).catch(function (err) {
        //console.log(err);
        response.writeHead(404, {'Content-Type': 'text/plain'});
        response.write("Not found");
        response.end();
    });
}).listen(5004, '127.0.0.1');