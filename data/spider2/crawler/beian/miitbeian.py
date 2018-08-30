# -*- coding: utf-8 -*-
import os, sys
import time
import random
import requests
from selenium import webdriver
import platform
from pyvirtualdisplay import Display
import StringIO
from PIL import Image

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../captcha'))
import captcha_miit

#logger
loghelper.init_logger("miitbeian", stream=True)
logger = loghelper.get_logger("miitbeian")

headers = {
    # must have, and must be the same!!!
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_showPage.action",
    # must have
    # "Cookie": "__jsluid=e228b1bd04a78de7b21c4713c81f7d1d; __jsl_clearance=1491540653.163|0|g1CsNq6jcFN60b2jOuP33nk6qVI%3D; JSESSIONID=9PVGwJx9BT47fWTOBeHJ6aUgInxXv-hr27YWHPmeEqnRwarQjwc-!-1834290836"
}


def get_webdriver(ip_port=None):
    system = platform.system()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-agent=" + headers["User-Agent"])
    if ip_port:
        chrome_options.add_argument('--proxy-server=%s' % ip_port)
    if system == "Darwin":
        driver = webdriver.Chrome("../../../selenium/chromedriver-mac", chrome_options=chrome_options)
    elif system == "Linux":
        chrome_options.binary_location = "/opt/google/chrome/google-chrome"
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        driver = webdriver.Chrome("/data/task-201606/geetest/chromedriver-linux", chrome_options=chrome_options)
    else:
        print "Wrong system"
        exit()

    # 在指定时间范围等待：
    driver.implicitly_wait(30)
    # 设置超时
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    return driver


def gen_cookie():
    url = "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_showPage.action"
    # 第一访问得到javascript生成cookie
    # display = Display(visible=0, size=(800, 600))
    # display.start()
    driver = get_webdriver()
    driver.get(url)
    # time.sleep(1)
    raw_cookies = driver.get_cookies()
    driver.quit()
    # display.stop()

    cookies = {}
    for c in raw_cookies:
        cookies[c["name"].encode("utf8")] = c["value"].encode("utf8")
        # logger.info(cookies)
    return cookies


def fetch_by_domain(session, cookies, domain):
    while True:
        # 获取验证码
        get_verify_code_url = "http://www.miitbeian.gov.cn/getVerifyCode?%s" % random.randint(0,100)
        r = session.get(get_verify_code_url, headers=headers, cookies=cookies)
        i = Image.open(StringIO.StringIO(r.content))
        i.save("vfimg/test.png")

        # OCR
        _, code = captcha_miit.process("vfimg/test.png")
        code = code.lower()
        logger.info("code=%s", code)
        if check_code(code) is False:
            continue

        # 验证
        valid_code_url = "http://www.miitbeian.gov.cn/common/validate/validCode.action"
        # post form data
        # validateValue: 3e6jzf
        # response {"result":true}
        payload = {"validateValue": code}
        r = session.post(valid_code_url, data=payload, headers=headers, cookies=cookies)
        logger.info(r.text)
        j = r.json()
        if j["result"]:
            break
        time.sleep(1)

    # 搜索
    search_url = "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_searchExecute.action"
    # post form data
    # siteName=&condition=1&siteDomain=teambition.com&siteUrl=&mainLicense=&siteIp=&unitName=&mainUnitNature=-1&certType=-1&mainUnitCertNo=&verifyCode=3dvx45
    payload = {
        "siteName": "",
        "condition": "1",
        "siteDomain": domain,
        "siteUrl": "",
        "mainLicense": "",
        "siteIp": "",
        "unitName": "",
        "mainUnitNature": "-1",
        "certType": "-1",
        "mainUnitCertNo": "",
        "verifyCode": code
    }
    r = session.post(search_url, data=payload, headers=headers, cookies=cookies)
    content = r.text
    # logger.info(content)
    # TODO parse

    result = util.re_get_result(r"doDetail\('(.*?)'\)", content)
    if result is not None:
        _id, = result
        logger.info("id: %s", _id)
        return _id
    else:
        return None


def check_code(code, length=6):
    if len(code) != length:
        return False
    code = code.lower()
    for c in code:
        if c >= "a" and c <="z":
            continue
        if c >= "0" and c <="9":
            continue
        return False
    return True


def fetch_by_id(session, cookies, _id):
    while True:
        # 获取详细验证码
        get_detail_verify_code_url = "http://www.miitbeian.gov.cn/getDetailVerifyCode?%s" % random.randint(0,100)
        r = session.get(get_detail_verify_code_url, headers=headers, cookies=cookies)
        i = Image.open(StringIO.StringIO(r.content))
        i.save("vfimg/test1.png")

        # OCR
        _, code = captcha_miit.process("vfimg/test1.png")
        code = code.lower()
        logger.info("code=%s", code)
        if check_code(code, 4) is False:
            continue

        #
        detail_url = "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_login.action"
        payload = {
            "verifyCode": code,
            "id": _id,
            "siteName": "",
            "siteDomain": "",
            "siteUrl": "",
            "mainLicense": "",
            "siteIp": "",
            "unitName": "",
            "mainUnitNature": "-1",
            "certType": "-1",
            "mainUnitCertNo": "",
            "bindFlag": "0"
        }
        r = session.post(detail_url, data=payload, headers=headers, cookies=cookies)
        content = r.text
        if "验证码错误，请重新输入" in content:
            continue

        logger.info(content)
        return content


def main(domain):
    cookies = gen_cookie()
    session = requests.Session()
    _id = fetch_by_domain(session, cookies, domain)
    content = fetch_by_id(session, cookies, _id)


def main1(_id):
    cookies = gen_cookie()
    session = requests.Session()
    content = fetch_by_id(session, cookies, _id)


if __name__ == "__main__":
    main("xiniudata.com")
    # main1("70780568")

