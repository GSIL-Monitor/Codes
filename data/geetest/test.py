#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-
import time
import random
import json
from StringIO import StringIO
from PIL import Image
import requests
import geetest



def request_getGtCaptcha(session):
    t = (int)(time.time()*1000)
    url = "http://antirobot.tianyancha.com/captcha/getGtCaptcha?t=%s" % t
    headers = {'Referer': 'http://antirobot.tianyancha.com/captcha/verify'}
    r = session.get(url, headers=headers)
    j = r.json()
    if j["success"] == 1:
        return j["gt"], j["challenge"], t

    return None


def request_geetest_getfrontlib(session, gt, t):
    url = "http://api.geetest.com/getfrontlib.php?gt=%s&callback=geetest_%s" % (gt, t)
    #headers = {'Referer': 'http://antirobot.tianyancha.com/captcha/verify'}
    headers = {'Referer': 'http://www.geetest.com/'}
    r = session.get(url, headers=headers)
    #print r.headers


def request_geetest_get(session, gt, challenge, t):
    url = "http://api.geetest.com/get.php?gt=%s" \
        "&challenge=%s" \
        "&product=embed&offline=false&type=slide" \
        "&callback=geetest_%s" \
        % (gt, challenge, t)
    #headers = {'Referer': 'http://antirobot.tianyancha.com/captcha/verify'}
    headers = {'Referer': 'http://www.geetest.com/'}
    r = session.get(url, headers=headers)
    t = r.text
    t = t.split("(")[1].split(")")[0]
    j = json.loads(t)
    return j

def download_image(session, url):
    #headers = {'Referer': 'http://antirobot.tianyancha.com/captcha/verify'}
    headers = {'Referer': 'http://www.geetest.com/'}
    r = session.get(url, headers=headers)
    img = Image.open(StringIO(r.content))
    return img


def request_geetest_ajax(session, actions, userresponse, gt, challenge, t):
    #headers = {'Referer': 'http://antirobot.tianyancha.com/captcha/verify'}
    headers = {'Referer': 'http://www.geetest.com/'}
    for action in actions:
        xpos = action["pos"]
        passTime = action["passtime"]
        actString = action["action"]
        imgLoadTime = random.randint(0, 200) + 50
        time.sleep( (passTime - imgLoadTime)/1000.0 )

        url = "http://api.geetest.com/ajax.php?" \
              "gt=%s" \
              "&challenge=%s" \
              "&userresponse=%s" \
              "&passtime=%s" \
              "&imgload=%s" \
              "&a=%s" \
              "&callback=geetest_%s" \
              % (gt, challenge, userresponse, passTime, imgLoadTime, actString, t)
        #print url

        r = session.get(url, headers=headers)
        #print r.request.headers
        str = r.text
        print str
        try:
            str = str.split("(")[1].split(")")[0]
            j = json.loads(str)
            if j["success"] == 1:
                return j
        except:
            pass

if __name__ == '__main__':
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:48.0) Gecko/20100101 Firefox/48.0'})
    session.headers.update({'Accept': '*/*'})
    session.headers.update({'Accept-Encoding': 'gzip, deflate, sdch'})
    session.headers.update({'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'})
    session.headers.update({'Connection': 'keep-alive'})

    # session_geetest = requests.Session()
    # session_geetest.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:48.0) Gecko/20100101 Firefox/48.0'})
    session_geetest = session

    # result = request_getGtCaptcha(session)
    # if result is None:
    #     print "Fail getGetCaptcha"
    #     exit()
    #
    # gt, challenge, t = result
    # print "gt: ", gt
    # print "challenge: ", challenge
    gt = "421b84eeaee7b2aed4c0ec5706d8b571"
    challenge = ""
    t = (int)(time.time()*1000)

    request_geetest_getfrontlib(session_geetest, gt, t)
    j = request_geetest_get(session_geetest, gt, challenge, t)
    print j
    bg_url = "http://%s%s" % (j["staticservers"][0], j["bg"])
    fullbg_url = "http://%s%s" % (j["staticservers"][0], j["fullbg"])
    bg = download_image(session_geetest, bg_url)
    fullbg = download_image(session_geetest, fullbg_url)

    bg = geetest.align_image(bg)
    fullbg = geetest.align_image(fullbg)
    #bg.show()
    #fullbg.show()

    xpos = geetest.get_position_x(bg, fullbg)
    print "xpos: ", xpos

    actions = geetest.get_actions(xpos)
    for action in actions:
        print "action: ", action

    userresponse = geetest.get_userresponse(xpos, j["challenge"])
    print "userresponse: ", userresponse

    result = request_geetest_ajax(session_geetest, actions, userresponse, gt, j["challenge"], t)
