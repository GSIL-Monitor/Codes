# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from pyquery import PyQuery as pq
import datetime, time
import json
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import proxy_pool
import db

#logger
loghelper.init_logger("haosou_index", stream=True)
logger = loghelper.get_logger("haosou_index")

cnt = 0
total = 0

def request(name, callback):
    global total
    proxy = {'type': 'http', 'anonymity':'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            time.sleep(60)

    if name is None:
        total -= 1
        logger.info(total)
        if total <= 0:
            begin()
        return
    url = 'http://index.so.com/index.php?a=overviewJson&q='+name+'&area=%E5%85%A8%E5%9B%BD'
    http_client.fetch(url, callback, proxy_host=proxy_ip["ip"], proxy_port=int(proxy_ip["port"]),request_timeout=10)

def handle_result(response, artifact):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        request(artifact['name'], lambda r,artifact=artifact:handle_result(r, artifact))
        # logger.info('erroring .....')
        return
    # logger.info(response.body)
    logger.info(response.request.url)
    try:
        result = json.loads(response.body)
        if result['status'] == 0:
            index = result['data'][0]['data']['month_index']
            if index == '-':
                index = 0
            save_index(artifact['id'], index)
    except:
        traceback.print_exc()

    total -= 1
    if total <= 0:
        begin()

def save_index(id, index):
    conn = db.connect_torndb()
    conn.update("update artifact set nameIndex=%s, nameIndexTime= now() where id =%s",
                index, id )
    conn.close()

def begin():
    global total, cnt
    conn = db.connect_torndb()

    artifacts = conn.query("select * from artifact order by id desc limit %s,1000", cnt)
    if len(artifacts) == 0:
        logger.info("Finish.")
        exit()

    for artifact in artifacts:
        logger.info(artifact["name"])
        cnt += 1
        total += 1
        request(artifact['name'], lambda r,artifact=artifact:handle_result(r, artifact))
    conn.close()


if __name__ == "__main__":
    logger.info("Start...")
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=30)
    begin()
    tornado.ioloop.IOLoop.instance().start()