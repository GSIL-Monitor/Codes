#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wechat import app
from flask import request, session, g, redirect, url_for, \
    abort, render_template,flash
from WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import time, datetime, random
import hashlib,md5
from goose import Goose
from goose.text import StopWordsChinese
import json
import requests

sAppID = "wxa3ce89070799e1be"
sAppSecret = "4d7b395b28810f03b572fe61fc6d961d"
sToken = "smh33TDLq30MrtZskrQRpLUrR6PJ8GJ"
sEncodingAESKey = "siLOMKbpW3XquvBAhOW7HBMn06lYYsQiPLEAMXziQsP"
organizationId = 1 #Gobi

@app.route("/")
def hello():
    return "Gobi Partners"

@app.route("/verify")
def verify():
    signature=request.args.get('signature', '')
    timestamp=request.args.get('timestamp', '')
    nonce=request.args.get('nonce', '')
    echostr=request.args.get('echostr', '')
    print signature
    print timestamp
    print nonce
    print echostr
    tmpArr=[]
    tmpArr.append(sToken)
    tmpArr.append(nonce)
    tmpArr.append(timestamp)
    tmpArr.sort()
    tmpStr = "".join(tmpArr)
    sha = hashlib.sha1()
    sha.update(tmpStr)
    if sha.hexdigest() == signature:
        return echostr
    else:
        print "signature error!"
        return ""
    

@app.route("/notify", methods=['GET', 'POST'])
def notify():
    signature=request.args.get('msg_signature', '')
    timestamp=request.args.get('timestamp', '')
    nonce=request.args.get('nonce', '')
    data=request.data
    #print signature
    #print timestamp
    #print nonce
    #print data

    wxcpt=WXBizMsgCrypt(sToken,sEncodingAESKey,sAppID)
    ret,sMsg=wxcpt.DecryptMsg( data, signature, timestamp, nonce)
    if(ret!=0):
        print "ERR: DecryptMsg ret: " + str(ret)
        return ""
    print sMsg

    xml_tree = ET.fromstring(sMsg)
    user = xml_tree.find("FromUserName").text
    app = xml_tree.find("ToUserName").text
    msgType = xml_tree.find("MsgType").text.lower()
    
    model = {}
    model["user"] = user
    model["app"] = app
    model["createTime"] = str((int)(time.time()))

    if msgType == "event":
        event = xml_tree.find("Event").text.lower()
        if event == "click":
            eventKey = xml_tree.find("EventKey").text.lower()
            if eventKey == "bind":
                userWechat = g.db.get('select * from user_wechat where wechatId=%s', user)
                if userWechat == None:
                    sRespData = render_template('bind.xml', model=model).encode("utf-8")
                else:
                    userId=userWechat["userId"]
                    user = g.db.get('select username from user where id=%s', userId)
                    sRespData = render_template('bound.xml', model=model, user=user).encode("utf-8")
                ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)   
                if( ret!=0 ):
                    print "ERR: EncryptMsg ret: " + ret
                    return ""
                return sEncryptMsg
        elif event == "subscribe":
            sRespData = render_template('subscribe.xml', model=model).encode("utf-8")
            ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
            if( ret!=0 ):
                print "ERR: EncryptMsg ret: " + ret
                return ""
            return sEncryptMsg
        elif event == "unsubscribe":
            pass
    elif msgType == "text":
        userWechat = g.db.get('select * from user_wechat where wechatId=%s', user)
        if userWechat == None:
            sRespData = render_template('bind.xml', model=model).encode("utf-8")
            ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)   
            if( ret!=0 ):
                print "ERR: EncryptMsg ret: " + ret
                return ""
            return sEncryptMsg

        content = xml_tree.find("Content").text
        #print content

        if content.isdigit():
            wechatMsg = g.db.get('select coldcallId, title, createTime from wechat_msg where userId=%s order by id desc limit 1',
                userWechat["userId"])
            if wechatMsg == None:
                return ""

            coldcallId = wechatMsg["coldcallId"]
            dt = datetime.datetime.today()
            print dt, wechatMsg["createTime"]
            if (dt - wechatMsg["createTime"]).seconds > 600:
                sRespData = render_template('changestatus_timeout.xml', model=model, title=wechatMsg["title"]).encode("utf-8")
                ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
                if( ret!=0 ):
                    print "ERR: EncryptMsg ret: " + ret
                    return ""
                return sEncryptMsg

            assignee = g.db.get("select * from user where id=%s", int(content))
            g.db.execute("delete from coldcall_user_rel where userIdentify=21020 and coldcallId=%s", coldcallId)
            g.db.insert('insert coldcall_user_rel(coldcallId,userId,userIdentify,createTime) \
                    values(%s,%s,%s,now())',
                    coldcallId,assignee["id"],21020)

            sRespData = render_template('changestatus.xml', model=model,title=wechatMsg["title"], assignee=assignee).encode("utf-8")
            ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
            if( ret!=0 ):
                print "ERR: EncryptMsg ret: " + ret
                return ""
            return sEncryptMsg
        else:
            sRespData = render_template('notprocess.xml', model=model).encode("utf-8")
            ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
            if( ret!=0 ):
                print "ERR: EncryptMsg ret: " + ret
                return ""
            return sEncryptMsg
    elif msgType == "link":
        userWechat = g.db.get('select * from user_wechat where wechatId=%s', user)
        if userWechat == None:
            sRespData = render_template('bind.xml', model=model).encode("utf-8")
            ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)   
            if( ret!=0 ):
                print "ERR: EncryptMsg ret: " + ret
                return ""
            return sEncryptMsg

        url = xml_tree.find("Url").text
        title = xml_tree.find("Title").text
        tilte_md5 = md5Str(title)
        description = xml_tree.find("Description").text

        coldcall = g.db.get("select * from coldcall where nameMd5=%s and organizationId=%s limit 1",tilte_md5,organizationId)
        if coldcall is not None:
            sRespData = render_template('exist.xml', model=model, title=title).encode("utf-8")
            ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
            if( ret!=0 ):
                print "ERR: EncryptMsg ret: " + ret
                return ""
            return sEncryptMsg

        if description == None or description == url:
            gs = Goose({'stopwords_class': StopWordsChinese})
            article = gs.extract(url=url)
            description = article.cleaned_text

        #print description
        dt = datetime.datetime.today()
        coldcallId = g.db.insert('insert coldcall(\
            organizationId,name,nameMd5,content,url,coldcallType,createTime\
            ) \
            values(\
                %s,%s,%s,%s,%s,24020,now() \
            )',
            organizationId, title, tilte_md5,description,url
        )
        #TODO only works for gobi

        print "coldcallId=", coldcallId
        g.db.insert('insert coldcall_user_rel(coldcallId,userId,userIdentify,createTime) \
            values(%s,%s,%s,now())',
            coldcallId,userWechat.userId,21010)
        g.db.insert('insert coldcall_user_rel(coldcallId,userId,userIdentify,createTime) \
            values(%s,%s,%s,now())',
            coldcallId,userWechat.userId,21030)

        wmId = g.db.insert('insert wechat_msg(userId,coldcallId,msgType,title,description,url,createTime) \
            values(%s,%s,%s,%s,%s,%s,now())',
            userWechat["userId"],coldcallId,"link",title,description,url);
        print "wmId=", wmId

        users = g.db.query("select u.* from user_organization_rel r join user u on u.id=r.userId where organizationId=%s and u.active !='D'",
                           organizationId)
        model["users"] = users

        msg = {"type":"coldcall", "id":coldcallId}
        print json.dumps(msg)
        try:
            g.kafkaProducer.send_messages("coldcall", json.dumps(msg))
        except:
            g.kafkaProducer.send_messages("coldcall", json.dumps(msg))

        sRespData = render_template('save.xml', model=model).encode("utf-8")
        ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
        if( ret!=0 ):
            print "ERR: EncryptMsg ret: " + ret
            return ""
        return sEncryptMsg
    else:
        sRespData = render_template('notprocess.xml', model=model).encode("utf-8")
        ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
        if( ret!=0 ):
            print "ERR: EncryptMsg ret: " + ret
            return ""
        return sEncryptMsg
        
    return ""


@app.route("/bind", methods=['GET', 'POST'])
def bind():
    if request.method=='GET':
        user=request.args.get('user', '')
        app=request.args.get('app', '')
        userWechat = g.db.get('select * from user_wechat where wechatId=%s', user)
        if userWechat == None:
            return render_template('bind.html', user=user)
        else:
            return render_template('bind_success.html')
    else:
        weixin_id = request.form['weixin_id']
        user_id = request.form['user_id']
        password = request.form['password']

        userEmail = g.db.get('select userId from user_email where email=%s', user_id)
        if userEmail == None:
            flash('login_fail')
            return redirect("/bind?user=%s" % weixin_id) 
        
        userId = userEmail["userId"]
        
        user = g.db.get('select username,password from user where id=%s', userId)
        SALT = "24114581331805856724"

        if md5Str("%s%s%s" % (SALT, userId, password.encode('utf-8'))) != user["password"].lower():
            session['user_id'] = user_id
            flash('login_fail')
            return redirect("/bind?user=%s" % weixin_id) 

        userWechat = g.db.get('select * from user_wechat where userId=%s', userId)
        if userWechat == None:
            g.db.execute('insert into user_wechat(userId,wechatId,createTime) values(%s,%s,now())',userId,weixin_id)
        else:
            g.db.execute('update user_wechat set wechatId=%s where userId=%s',weixin_id, userId)
        return render_template('bind_success.html')

@app.route("/help")
def help():
    return "help"


ACCESS_TOKEN = None
ACCESS_TOKEN_TIME = 0
JSAPI_TICKET = None

jsappid="wxa3ce89070799e1be"
jsappsecret="4d7b395b28810f03b572fe61fc6d961d"

#戈壁创投 订阅号
#AppID(应用ID)wxb5082f39e27c0543
#AppSecret(应用密钥)1f89504096f6511db6f5a76aa695148c
@app.route("/api/wechat/config/get", methods=['GET', 'POST'])
def api_wechat_config_get():
    global ACCESS_TOKEN, JSAPI_TICKET, ACCESS_TOKEN_TIME

    request_json = request.get_json()

    if ACCESS_TOKEN is None or JSAPI_TICKET is None or ACCESS_TOKEN_TIME + 7000 < time.time():
        print "get ACCESS_TOKEN and JSAPI_TICKET"
        ACCESS_TOKEN_TIME = time.time()
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (jsappid,jsappsecret)
        retry = 0
        while True:
            if retry > 3:
                break
            retry += 1
            try:
                r = requests.get(url)
            except:
                time.sleep(2)
                continue
            if r.status_code != 200:
                time.sleep(2)
                continue
            break
        if r is None or r.status_code != 200:
            return "{}"
        j = r.json()
        ACCESS_TOKEN = j["access_token"]

        url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % ACCESS_TOKEN
        #print url
        retry = 0
        while True:
            if retry > 3:
                break
            retry += 1
            try:
                r = requests.get(url)
            except:
                time.sleep(2)
                continue
            if r.status_code != 200:
                time.sleep(2)
                continue
            break
        if r is None or r.status_code != 200:
            return "{}"
        j = r.json()
        JSAPI_TICKET = j["ticket"]
        print JSAPI_TICKET

    noncestr = "".join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789',16))
    timestamp = int(time.time())
    url = request_json["url"]
    str = "jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s" % (JSAPI_TICKET, noncestr, timestamp, url)
    print str
    sha1 = hashlib.sha1()
    sha1.update(str)
    signature = sha1.hexdigest()
    print signature
    result = {
        "appId":jsappid,
        "timestamp":timestamp,
        "nonceStr":noncestr,
        "signature":signature
    }
    return json.dumps(result)


def md5Str(str):
    m = md5.new()
    m.update(str.encode('utf-8'))
    return m.hexdigest()