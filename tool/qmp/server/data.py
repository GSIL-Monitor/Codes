from flask import Flask, request, jsonify
import json
import datetime
import md5
from pymongo import MongoClient
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)

@app.route("/data/save", methods=['POST'])
def save():
    playload = request.json
    url = playload["payload"]["url"]
    tmps = url.split("?")
    url = tmps[0]
    post_data = playload["payload"]["postdata"]
    data = playload["payload"]["data"]
    data_md5 = get_md5_str(data)
    app.logger.info(url)
    # app.logger.info(post_data)
    # app.logger.info(data)

    data_json = json.loads(data, "utf8")
    fix_json(data_json)

    mongo = connect_mongo()
    item = mongo.raw.qmp.find_one({"datamd5": data_md5})
    if item is None:
        result = {
            "url": url,
            "postdata": json.loads(post_data, "utf8"),
            "data": data_json,
            "createTime": datetime.datetime.utcnow(),
            "datamd5":data_md5,
        }
        # app.logger.info(result)
        mongo.raw.qmp.insert_one(result)
    return "ok"


def get_md5_str(data):
    m = md5.new()
    m.update(data)
    return m.hexdigest()


def connect_mongo():
    # PyMongo is thread-safe and provides built-in connection pooling for threaded applications.
    conn_addr1 = "dds-2ze211ee68246e341.mongodb.rds.aliyuncs.com:3717"
    conn_addr2 = "dds-2ze211ee68246e342.mongodb.rds.aliyuncs.com:3717"
    replicat_set = "mgset-1321009"
    username = "root"
    password = "tb67168"

    client = MongoClient([conn_addr1, conn_addr2], replicaSet=replicat_set,
                         maxPoolSize=20, maxIdleTimeMS=10000, waitQueueTimeoutMS=5000)
    client.admin.authenticate(username, password)
    return client


def fix_json(js):
    if isinstance(js, dict):
        for key in js.keys():
            if "." in key:
                print key
                value = js.get(key)
                key1 = key.replace(".", "_")
                js[key1] = value
                js.pop(key)
            fix_json(js.get(key))
    elif isinstance(js, list):
        for item in js:
            fix_json(item)


if __name__ == "__main__":
    app.run(host='59.110.22.58', port=5001, debug=True)
