#!/usr/local/bin/python
# -*- coding: utf8 -*-
# http://www.w2bc.com/article/170660
# download https://sites.google.com/a/chromium.org/chromedriver/home
# put chromedrive in path such as /usr/local/bin
#
# firefox
# https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette/WebDriver
# mv /usr/local/bin/geckodriver /usr/local/bin/wires

import os, sys
import datetime
import traceback
import chardet
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import PIL.Image as image
import time,re,cStringIO,urllib2,random
import math
import platform
from pyvirtualdisplay import Display

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import db

reload(sys)
sys.setdefaultencoding("utf-8")

def get_merge_image(filename,location_list):
    '''
    根据位置对图片进行合并还原
    :filename:图片
    :location_list:图片位置
    '''
    im = image.open(filename)

    new_im = image.new('RGB', (260,116))

    im_list_upper=[]
    im_list_down=[]

    for location in location_list:

        if location['y']==-58:
            pass
            im_list_upper.append(im.crop((abs(location['x']),58,abs(location['x'])+10,166)))
        if location['y']==0:
            pass

            im_list_down.append(im.crop((abs(location['x']),0,abs(location['x'])+10,58)))

    new_im = image.new('RGB', (260,116))

    x_offset = 0
    for im in im_list_upper:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]

    x_offset = 0
    for im in im_list_down:
        new_im.paste(im, (x_offset,58))
        x_offset += im.size[0]

    return new_im


def get_image(driver,div):
    '''
    下载并还原图片
    :driver:webdriver
    :div:图片的div
    '''
    #找到图片所在的div
    background_images=driver.find_elements_by_xpath(div)

    location_list=[]

    imageurl=''

    for background_image in background_images:
        location={}

        #在html里面解析出小图片的url地址，还有长高的数值
        location['x']=int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][1])
        location['y']=int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][2])
        imageurl=re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][0]

        location_list.append(location)

    imageurl=imageurl.replace("webp","jpg")
    print imageurl

    jpgfile=cStringIO.StringIO(urllib2.urlopen(imageurl).read())

    #重新合并图片
    image=get_merge_image(jpgfile,location_list )

    return image


def is_similar(image1,image2,x,y):
    '''
    对比RGB值
    '''
    pixel1=image1.getpixel((x,y))
    pixel2=image2.getpixel((x,y))

    for i in range(0,3):
        if abs(pixel1[i]-pixel2[i])>=50:
            return False

    return True


def get_diff_location(image1,image2):
    '''
    计算缺口的位置
    '''
    i=0

    for i in range(0,260):
        for j in range(0,116):
            if is_similar(image1,image2,i,j)==False:
                return  i


def get_track1(distance):
    _id = None
    mongo = db.connect_mongo()
    track = mongo.raw.tyc_real_track.find_one({"loc": distance}, sort=[("_id", -1)])
    if track is None:
        track = mongo.raw.tyc_real_track.find_one({"loc": {"$gt":distance}}, sort=[("loc", 1), ("_id", -1)])
        if track is not None:
            print "拟合: %s" % (track["loc"])
            diff = track["loc"] - distance
            # i = (len(track["track"])-diff)/2
            i = 10
            while diff != 0:
                # (x,y,t,s) = track["track"][i]
                (x, y, t) = track["track"][i]
                if x <= 0:
                    i += 1
                    continue
                if x <= diff:
                    del track["track"][i]
                    diff -= x
                else:
                    i += 1
                print "len: %s , i: %s" % (len(track["track"]), i)
                if i >= len(track["track"])-10:
                    break
            print "拟合完毕"
    else:
        _id = track["_id"]
    mongo.close()

    if track is not None:
        list = []
        # a = 1.0 + random.randint(-1000,1000)/10000.0
        a = 1
        for x,y,t in track["track"]:
            # list.append((x,y,t*a,stage))
            list.append((x, y, t * a))
        return list, _id
    return None


def crack(ip_port):
    global display
    flag = False
    retries = 0
    try:
        system = platform.system()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')
        if ip_port:
            chrome_options.add_argument('--proxy-server=%s' % ip_port)
        if system == "Darwin":
            driver = webdriver.Chrome("./chromedriver-mac", chrome_options=chrome_options)
        elif system == "Linux":
            chrome_options.binary_location = "/opt/google/chrome/google-chrome"
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-setuid-sandbox")
            driver = webdriver.Chrome("./chromedriver-linux", chrome_options=chrome_options)
        else:
            print "Wrong system"
            exit()

        # profile_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], "./profile")
        # fp = webdriver.FirefoxProfile(profile_dir)
        # # fp.set_preference('network.proxy.type', 1)   #默认值0，就是直接连接；1就是手工配置代理。
        # # fp.set_preference('network.proxy.socks_version', socks_version)
        # # fp.set_preference('network.proxy.socks', socks_ip)
        # # fp.set_preference('network.proxy.socks_port', socks_port)
        # fp.update_preferences()
        # if system == "Darwin":
        #     driver = webdriver.Firefox(firefox_profile=fp, executable_path="./geckodriver-mac")
        # elif system == "Linux":
        #     driver = webdriver.Firefox(firefox_profile=fp, executable_path="./geckodriver-linux", firefox_binary="/opt/firefox/firefox")
        # else:
        #     print "Wrong system"
        #     exit()

        # dcap = dict(DesiredCapabilities.PHANTOMJS)
        # dcap["phantomjs.page.settings.userAgent"] = (
        #     "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36"
        # )
        # ps = ip_port.split("://")
        # print ps[0]
        # print ps[1]
        # service_args = [
        #     '--proxy=%s' % ps[1],
        #     '--proxy-type=%s' % ps[0],
        # ]
        # driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)

        # driver.set_window_size(1280,800)
        # 在指定时间范围等待：
        driver.implicitly_wait(30)
        # 设置超时
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)


        # 打开网页
        driver.get("http://antirobot.tianyancha.com/captcha/verify")

        while True:
            retries += 1
            if retries > 5:
                return False

            # 等待页面的上元素刷新出来
            WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_xpath(
                "//div[@class='gt_slider_knob gt_show']").is_displayed())
            WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_xpath(
                "//div[@class='gt_cut_bg gt_show']").is_displayed())
            WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_xpath(
                "//div[@class='gt_cut_fullbg gt_show']").is_displayed())

            #driver.save_screenshot('screenshot.png')
            #print driver.page_source
            # 下载图片
            print "开始下载图片"
            image1=get_image(driver, "//div[@class='gt_cut_bg gt_show']/div")
            image2=get_image(driver, "//div[@class='gt_cut_fullbg gt_show']/div")

            # 计算缺口位置
            loc=get_diff_location(image1, image2)
            if loc is None:
                driver.refresh()
                continue

            loc -= 5
            print "位置: %s" % loc

            if loc < 10:
                driver.quit()
                return False

            # 生成x的移动轨迹点
            track_list=get_track1(loc)
            if track_list is None:
                driver.refresh()
                continue
            track_list, _id = track_list

            # 找到滑动的圆球
            print "找到滑动的圆球"
            ball_element=driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")

            # 鼠标点击元素并按住不放
            print "第一步，点击元素"
            ActionChains(driver).move_to_element(ball_element).perform()
            ActionChains(driver).move_by_offset(random.randint(-5,5),random.randint(-5,5)).perform()
            ActionChains(driver).click_and_hold().perform()
            #driver.save_screenshot('screenshot1.png')

            print "第二步，拖动元素"
            for x,y,t in track_list:
                time.sleep(t/1000.0)
                ActionChains(driver).move_by_offset(x, y).perform()

            print "第三步，释放鼠标"
            # 释放鼠标
            t = random.randint(400,500) / 1000.0
            time.sleep(t)
            ActionChains(driver).release().perform()

            time.sleep(2)
            #driver.save_screenshot('screenshot3.png')

            try:
                element = driver.find_element_by_class_name('gt_info_text')
                raw_status = element.text

                if isinstance(raw_status, unicode):
                    status = raw_status
                else:
                    print chardet.detect(raw_status)
                    try:
                        status = raw_status.decode("utf8")
                    except:
                        status = raw_status.decode("gbk")

                print u"破解验证码的结果: ", status

                if not status or status.find(u'错误') > -1:
                    driver.refresh()
                    continue
                elif status.find(u'失败') > -1 or \
                     status.find(u'怪物') > -1:
                    if _id is not None:
                        mongo = db.connect_mongo()
                        t = mongo.raw.tyc_real_track.find_one({"_id":_id})
                        fail_times = t.get("fail_times")
                        if fail_times is None:
                            fail_times = 1
                        else:
                            fail_times += 1
                        # if fail_times>=5:
                        #     mongo.raw.tyc_real_track.delete_one({"_id":_id})
                        # else:
                        mongo.raw.tyc_real_track.update_one({"_id":_id}, {"$set":{"fail_times": fail_times}})
                        mongo.close()
                elif status.find(u'验证通过') > -1:
                    mongo = db.connect_mongo()
                    data = {
                        "loc": loc,
                        "track": track_list
                    }
                    t = mongo.raw.tyc_real_track.find_one({"loc":loc})
                    if t is None:
                        # mongo.raw.tyc_real_track.insert_one(data)
                        pass
                    else:
                        mongo.raw.tyc_real_track.update_one({"_id": _id}, {"$set": {"fail_times": 0}})
                    mongo.close()

                    # 点击验证
                    print "第四步，提交"
                    submit=driver.find_element_by_xpath("//button[@id='submit-button']")
                    ActionChains(driver).click(on_element=submit).perform()
                    time.sleep(3)
                    flag = True
                    break
                else:
                    driver.quit()
                    return False

                time.sleep(3.5)
                refresh_element = driver.find_element_by_xpath("//a[@class='gt_refresh_button']")
                ActionChains(driver).click(on_element=refresh_element).perform()
                time.sleep(0.5)
                continue
            except:
                print "Fail"
                traceback.print_exc()
                # driver.refresh()
                # time.sleep(random.randint(1500,2000)/1000.0)
                driver.quit()
                if system != "Darwin":
                    display.stop()
                    display = Display(visible=0, size=(800, 600))
                    display.start()
                    time.sleep(5)
                return flag
    except selenium.common.exceptions.TimeoutException, exception:
        print "Timeout"
    except socket.timeout:
        print "Timeout"
    except Exception, e:
        traceback.print_exc()

    try:
        driver.quit()
    except:
        pass
    return flag


def crack_all():
    while True:
        mongo = db.connect_mongo()
        cnt = mongo.raw.proxy_tyc.count()
        mongo.close()
        if cnt >= NUM:
            print "reach %s, stop crack" % NUM
            time.sleep(60)
            continue

        mongo = db.connect_mongo()
        proxies = list(mongo.raw.proxy.find({"$or": [{"http_type": "Socks5"}, {"http_type": "Socks4"}]},
                                            sort=[("_id", 1)]))
        mongo.close()
        for proxy in proxies:
            ip_port = proxy["ip:port"].split(":")
            ip = ip_port[0]
            port = int(ip_port[1])
            mongo = db.connect_mongo()
            p = mongo.raw.proxy_tyc.find_one({"ip":ip, "port":port})
            mongo.close()

            if p is None:
                socks_url = "%s://%s" % (proxy["http_type"].lower(), proxy["ip:port"])
                print socks_url
                flag = crack(socks_url)
                if flag:
                    data = {"ip": ip,
                            "port": port,
                            "type": proxy["http_type"],
                            "createTime": datetime.datetime.utcnow()
                            }
                    mongo = db.connect_mongo()
                    mongo.raw.proxy_tyc.insert(data)
                    cnt = mongo.raw.proxy_tyc.count()
                    mongo.close()
                    if cnt >= NUM:
                        break

NUM=20

if __name__ == '__main__':
    # tyc_crack.py socks4://183.136.213.96:1080
    import socket
    socket.setdefaulttimeout(60)

    system = platform.system()
    if system != "Darwin":
        display = Display(visible=0, size=(800, 600))
        display.start()

    time.sleep(5)
    try:
        if len(sys.argv) != 2:
            crack(None)
        elif sys.argv[1] == "all":
            crack_all()
        else:
            crack(sys.argv[1])
    finally:
        if system != "Darwin":
            display.stop()