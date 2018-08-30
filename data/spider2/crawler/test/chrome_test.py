# -*- coding: utf-8 -*-
import platform
from pyvirtualdisplay import Display
from selenium import webdriver
import time


def get_url():

    system = platform.system()
    if system != "Darwin":
        print "her1"
        display = Display(visible=0, size=(800, 600))
        display.start()

    # system = platform.system()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')

    # chrome_options.add_argument('accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    if system == "Darwin":
        driver = webdriver.Chrome("./chromedriver-mac", chrome_options=chrome_options)
    elif system == "Linux":
        chrome_options.binary_location = "/opt/google/chrome/google-chrome"
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        # driver = webdriver.Chrome("./chromedriver-linux", chrome_options=chrome_options)
        driver = webdriver.Chrome("/data/task-201606/spider2/crawler/test/chromedriver-linux", chrome_options=chrome_options)

        print "here"
    else:
        print "Wrong system"
        exit()

    driver.get('https://www.8btc.com/news')
    time.sleep(60)
    print driver.page_source
    print "done"
    raw_cookies = driver.get_cookies()
    driver.quit()
    # display.stop()

    cookie = [item["name"] + "=" + item["value"] for item in raw_cookies]
    if cookie is not None:
        cookiestr = ';'.join(item for item in cookie)
        # print('cookie:', cookiestr)
        if cookiestr.find('D_HID') >= 0 or cookiestr.find('_ok') >= 0:
            print(cookiestr)
            Cookie = cookiestr
            return Cookie
    return None
    # cookies = {}
    # for c in raw_cookies:
    #     cookies[c["name"].encode("utf8")] = c["value"].encode("utf8")
    # print cookies
    # return cookies
    # return driver


system = platform.system()
if system != "Darwin":
    print "her1"
    display = Display(visible=0, size=(800, 600))
    display.start()

time.sleep(5)
get_url()