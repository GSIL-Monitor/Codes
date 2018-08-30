from flask import request, make_response, json, g, current_app
import hashlib, datetime,os, sys

from . import bp

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
import loghelper
import datetime

# logger
loghelper.init_logger("stat", stream=True)
logger = loghelper.get_logger("stat")


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)




@bp.route('/get', methods=['GET'])
def list():
    # user = g.user
    # payload = request.json.get("payload")
    # if payload is None:
    #     result = {"code": 1}
    #     return json.dumps(result)

    # code = payload.get("code")
    #
    # sql = "select * from company " \
    #       " where (active = 'Y' or active is null)" \
    #       " and code = %s"
    # company = g.conn.get(sql, code)

    sql = "select * from spider_stats order by id desc limit 10"

    data = g.conn_crawler.query(sql)

    result = {"code": 0,
              "data": data,
              }
    return json.dumps(result)


@bp.route('/gettest', methods = ['GET', 'POST'])
def listtest():
    # user = g.user
    print "adddd"
    print request.data
    print "dddddddd"
    payload = json.loads(request.data).get("products")
    if payload is None:
        result = {"code": 1}
        return json.dumps(result)

    # code = payload.get("code")
    #
    # sql = "select * from company " \
    #       " where (active = 'Y' or active is null)" \
    #       " and code = %s"
    # company = g.conn.get(sql, code)

    else:
        return json.dumps(payload,ensure_ascii=False, cls=CJsonEncoder)
