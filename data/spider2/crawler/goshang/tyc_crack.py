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
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import PIL.Image as image
import time,re,cStringIO,urllib2,random
from pyvirtualdisplay import Display
import pymongo
import math

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db, loghelper

#logger
loghelper.init_logger("tyc_crack", stream=True)
logger = loghelper.get_logger("tyc_crack")


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
        # location['x']=int(re.findall("background-image: url\((.*)\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][1])
        # location['y']=int(re.findall("background-image: url\((.*)\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][2])
        # imageurl=re.findall("background-image: url\((.*)\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][0]
        location['x']=int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][1])
        location['y']=int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][2])
        imageurl=re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",background_image.get_attribute('style'))[0][0]

        location_list.append(location)

    imageurl=imageurl.replace("webp","jpg")
    logger.info(imageurl)

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


def get_track(length):
    '''
    根据缺口的位置模拟x轴移动的轨迹
    '''
    list=[]

    # 间隔通过随机范围函数来获得
    x=random.randint(2,4)

    while length-x>=5:
        list.append(x)

        length=length-x
        x=random.randint(2,4)

    for i in xrange(length):
        list.append(1)

    return list


def crack(socks_version, socks_ip, socks_port):
    flag = False
    while True:
        try:
            profile_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], "./profile")
            logger.info(profile_dir)
            fp = webdriver.FirefoxProfile(profile_dir)
            fp.set_preference('network.proxy.type', 1)   #默认值0，就是直接连接；1就是手工配置代理。
            fp.set_preference('network.proxy.socks_version', socks_version)
            fp.set_preference('network.proxy.socks', socks_ip)
            fp.set_preference('network.proxy.socks_port', socks_port)
            fp.update_preferences()
            driver = webdriver.Firefox(firefox_profile=fp)
            logger.info("driver start")
            time.sleep(5)

            # 在指定时间范围等待：
            driver.implicitly_wait(30)
            # 设置超时
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)


            # 打开网页
            driver.get("http://antirobot.tianyancha.com/captcha/verify")
            logger.info("get web page")
            #driver.get("http://www.tianyancha.com/company/1676729283")
            # driver.get("http://www.ip138.com")

            # time.sleep(5)
            # driver.save_screenshot('screenshot.png')
            # 等待页面的上元素刷新出来
            WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']").is_displayed())
            WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_bg gt_show']").is_displayed())
            WebDriverWait(driver, 10).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_fullbg gt_show']").is_displayed())

            while True:
                #driver.save_screenshot('screenshot.png')
                #print driver.page_source
                # 下载图片
                logger.info("开始下载图片")
                image1=get_image(driver, "//div[@class='gt_cut_bg gt_show']/div")
                image2=get_image(driver, "//div[@class='gt_cut_fullbg gt_show']/div")

                # 计算缺口位置
                loc=get_diff_location(image1, image2)
                logger.info("位置: %s",loc)

                # 生成x的移动轨迹点
                loc -= 5
                back = 20
                loc += back
                track_list=get_track(loc)

                # 找到滑动的圆球
                element=driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                location=element.location
                # 获得滑动圆球的高度
                y=location['y']
                y=445

                # 鼠标点击元素并按住不放
                logger.info("第一步，点击元素")
                ActionChains(driver).click_and_hold(on_element=element).perform()
                time.sleep(random.randint(200,500)/1000.0)
                driver.save_screenshot('logs/screenshot1.png')

                logger.info("第二步，拖动元素")
                track_string = ""
                num = 0
                for track in track_list:
                    #logger.info( "%d,%d", track, y - 445 )
                    track_string = track_string + "{%d,%d}," % (track, y - 445)
                    # # xoffset=track+22:这里的移动位置的值是相对于滑动圆球左上角的相对值，而轨迹变量里的是圆球的中心点，所以要加上圆球长度的一半。
                    # # yoffset=y-445:这里也是一样的。不过要注意的是不同的浏览器渲染出来的结果是不一样的，要保证最终的计算后的值是22，也就是圆球高度的一半
                    # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=track+22, yoffset=y-445 + _y).perform()
                    # # 间隔时间也通过随机函数来获得
                    # # t = random.randint(10,50)/1000.0
                    # t = random.randint(5,20)/1000.0
                    #print t
                    if num < loc*0.75:
                        base = abs(num - loc*0.75)
                    else:
                        base = abs(num - loc*0.75)*3
                    base = math.sqrt(base)
                    base = math.pow(base,1.2)
                    t = base/1000.0
                    t = t * 100/loc

                    if t < 0.001:
                        t = 0.001
                    logger.info( t )
                    time.sleep(t)
                    ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=track+22, yoffset=y-445).perform()

                    num += track
                logger.info(track_string)

                # xoffset=21，本质就是向后退一格。这里退了5格是因为圆球的位置和滑动条的左边缘有5格的距离
                # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y-445).perform()
                # time.sleep(0.1)
                # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y-445).perform()
                # time.sleep(0.1)
                # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y-445).perform()
                # time.sleep(0.1)
                # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y-445).perform()
                # time.sleep(0.1)
                # ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=y-445).perform()
                t = random.randint(200,300)/1000.0
                logger.info( t )
                time.sleep(t)

                t = random.randint(15,18)/1000.0
                logger.info( t )
                for i in range(0,10):
                    ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=22-1, yoffset=y-445).perform()
                    time.sleep(t)

                t = random.randint(23,25)/1000.0
                logger.info( t )
                for i in range(0,7):
                    ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=22-1, yoffset=y-445).perform()
                    time.sleep(t)

                t = random.randint(25,28)/1000.0
                logger.info( t )
                for i in range(0,3):
                    ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=22-1, yoffset=y-445).perform()
                    time.sleep(t)

                driver.save_screenshot('logs/screenshot2.png')
                logger.info("第三步，释放鼠标")
                # 释放鼠标
                t = random.randint(120,150)/1000.0
                time.sleep(t)
                ActionChains(driver).release(on_element=element).perform()

                time.sleep(3)
                driver.save_screenshot('logs/screenshot3.png')

                # 点击验证
                # submit=driver.find_element_by_xpath("//button[@id='submit-button']")
                # ActionChains(driver).click(on_element=submit).perform()
                try:
                    driver.find_element_by_xpath("//div[@class='gt_ajax_tip success']")
                    logger.info( "Good" )
                    # 点击验证
                    logger.info( "第四步，提交" )
                    submit=driver.find_element_by_xpath("//button[@id='submit-button']")
                    ActionChains(driver).click(on_element=submit).perform()
                    time.sleep(5)
                    flag = True
                    break
                except:
                    logger.info( "Fail" )
                    refresh_element=driver.find_element_by_xpath("//a[@class='gt_refresh_button']")
                    ActionChains(driver).click(on_element=refresh_element).perform()
                    time.sleep(random.randint(1500,2000)/1000.0)
        except selenium.common.exceptions.TimeoutException, exception:
            logger.info("Timeout")
            break
        except selenium.common.exceptions.WebDriverException, exception:
            logger.info(exception)

        try:
            driver.quit()
        except:
            pass

        if flag:
            break
    try:
        driver.quit()
    except:
        pass

    return flag


def test_all():
    mongo = db.connect_mongo()
    proxies = list(mongo.raw.proxy.find({"$or":[{"http_type":"Socks5"},{"http_type":"Socks4"}]}, sort=[("_id",pymongo.ASCENDING)]))
    #proxies = list(mongo.raw.proxy.find({"http_type":"Socks4"}, sort=[("_id",pymongo.ASCENDING)]))
    mongo.close()
    for proxy in proxies:
        socks_version = 4
        if proxy["http_type"] == "Socks5":
            socks_version = 5
        ip_port = proxy["ip:port"].split(":")
        ip = ip_port[0]
        port = int(ip_port[1])
        conn = db.connect_torndb_crawler()
        p = conn.get("select * from proxy_tyc where ip=%s and port=%s", ip, port)
        conn.close()

        if p is None:
            logger.info("Socks%s://%s:%s" % (socks_version, ip, port))
            flag = crack(socks_version, ip, port)
            if flag:
                logger.info("Good!")
                conn = db.connect_torndb_crawler()
                conn.insert("insert proxy_tyc(ip,port,type,createTime) values(%s,%s,%s,now())",
                            ip, port,proxy["http_type"])
                cnt = conn.get("select count(*) cnt from proxy_tyc")
                conn.close()
                if cnt["cnt"] >= 2:
                    break


if __name__ == '__main__':
    # tyc_crack.py socks4://183.136.213.96:1080
    display = Display(visible=0, size=(1280, 800))
    display.start()
    time.sleep(5)
    while True:
        conn = db.connect_torndb_crawler()
        cnt = conn.get("select count(*) cnt from proxy_tyc")
        conn.close()
        if cnt["cnt"] >= 3:
            time.sleep(60)
            continue
        test_all()
    display.stop()

    '''
    if len(sys.argv) != 2:
        print "python tyc_crack.py socks4://218.20.227.183:1080"
        exit()
    socks = sys.argv[1]
    ss = socks.split("://")
    ip_port = ss[1].split(":")
    socks_version = 4
    if ss[0] == "socks5":
        socks_version = 5
    crack(socks_version, ip_port[0], int(ip_port[1]))
    '''