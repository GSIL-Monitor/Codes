from flask import Flask,g
import torndb
from kafka import (KafkaClient, SimpleProducer)

#configuration
SECRET_KEY = '234r;a;sdf-21-a'

#create our little application
app = Flask(__name__)
app.config.from_object(__name__)

import dbconfig
import kafkaconfig

def connect_db():
    return torndb.Connection(dbconfig.DB_HOST,
                      dbconfig.DB_NAME,
                      dbconfig.DB_USER,
                      dbconfig.DB_PASSWD,
                      time_zone='+8:00');

@app.before_request
def before_request():
    #print "before_request"
    g.db = connect_db()
    g.kafka = KafkaClient(kafkaconfig.KAFKA_SERVERS)
    g.kafkaProducer = SimpleProducer(g.kafka)
    pass

@app.teardown_request
def teardown_request(exception):
    #print "teardown_request"
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    kafka = getattr(g, 'kafka', None)
    if kafka is not None:
        kafka.close()
    pass

import wechat.views.bind

