# -*- coding: utf-8 -*-
import json
import os, sys
import time
import random
import requests
from selenium import webdriver
import StringIO
from PIL import Image
import captcha_miit
from pyquery import PyQuery as pq
from lxml import html

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, util, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


headers = {
    "User-Agent": 'User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_showPage.action",
    }
headers1 = {
    "User-Agent": 'User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0',
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_searchExecute.action",
    "Host":"www.miitbeian.gov.cn",
    }

def get_proxy(http_type):
    proxy = {'type': http_type, 'anonymity': 'high'}
    proxy_ip = None
    while proxy_ip is None:
        print("Start proxy_pool.get_single_proxy")
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            print("proxy_pool.get_single_proxy return None")
        print(proxy_ip['ip:port'])
        return {proxy_ip['ip']:proxy_ip['port']}

def get_webdriver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=" + headers["User-Agent"])
    options.binary_location = '/root/firefox/firefox'

    driver = webdriver.Firefox(firefox_options=options,executable_path='./geckodriver',proxy=get_proxy('http'))
    # 在指定时间范围等待：
    driver.implicitly_wait(30)
    # 设置超时
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    return driver

def __clear_brs():
    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep firefox').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))

    gcs = map(lambda y: str(y[1]),
              filter(lambda x: int(x[2]) == 1,
                     [line.split() for line in os.popen('ps -ef | grep Xvfb').readlines()]))
    if gcs:
        os.popen('kill %s' % ' '.join(gcs))

    print('clear firefox done')

def get_cookie():
    cookies_result = {'status':'wrong','cookies':None}
    retry = 0
    while True:
        retry += 1
        if retry > 5:
            return cookies_result
        try:
            print('to get cookie...')
            url = "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_showPage.action"
            driver = get_webdriver()
            driver.get(url)
            raw_cookies = driver.get_cookies()
            driver.quit()
            # __clear_brs()

            cookies = {}
            for c in raw_cookies:
                cookies[c["name"].encode("utf8")] = c["value"].encode("utf8")
            print(cookies)
            if cookies.has_key('__jsluid') and cookies.has_key('JSESSIONID'):
                cookies_result['status'] = 'got'
                cookies_result['cookies'] = cookies
                return cookies_result
        except Exception as e:
            print('driver error :%s',e)
            raise e
            # __clear_brs()

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

def get_verify_code(session, cookies):
    # 计数 {} 次数
    res = 0
    while True:
        res += 1
        if res > 20:
            return None
        # get verify_code
        img_path = "vfimg/test.png"
        try:
            verify_code_url = "http://www.miitbeian.gov.cn/getVerifyCode?%s" % random.randint(0, 100)
            r = session.get(verify_code_url, headers=headers1, cookies=cookies, proxies=get_proxy('http'),timeout=10)
            i = Image.open(StringIO.StringIO(r.content))
            i.save(img_path)
            global C
            C += 1
            save('C',C)
            _, code = captcha_miit.process(img_path)
            code = code.lower()
            print("code=%s" % code)
            if check_code(code) is False:
                continue


            # 验证
            valid_code_url = "http://www.miitbeian.gov.cn/common/validate/validCode.action"
            payload = {"validateValue": code}
            r = session.post(valid_code_url, data=payload, headers=headers1, cookies=cookies, proxies=get_proxy('http'),timeout=10)

            print(r.text)
            j = r.json()

            if j.has_key('result') is False:
                continue
            if j['result']:
                global D
                D += 1
                save('D',D)
                return code
        except:
            pass

def get_pages(session, cookies, fullname):
    page_result = {'status':None,'pages':None,'proxies':None}
    code = get_verify_code(session, cookies)
    if code is None:
        page_result['status'] = 'nocode'
        return page_result
    time.sleep(2)
    # 搜索
    res = 0
    while True:
        res +=1
        if res >10 :
            page_result['status'] = 'nopage'
            return page_result

        try:
            unitname = fullname.encode('gb2312','ignore')
            search_url = "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_searchExecute.action"
            payload = {
                "siteName": "",
                "condition": "5",
                "siteDomain": '',
                "siteUrl": "",
                "mainLicense": "",
                "siteIp": "",
                "unitName": unitname,
                "mainUnitNature": "-1",
                "certType": "-1",
                "mainUnitCertNo": "",
                "verifyCode": code
            }
            proxies = get_proxy('http')
            r = session.post(search_url, data=payload, headers=headers, cookies=cookies,proxies=proxies,timeout=10)
            content = r.text

            if content.find("备案信息查询") >= 0:
                if content.find('没有符合条件的记录') == -1:
                    result = util.re_get_result(r"1/(\d+)", content)
                    if result is not None:
                        pages, = result
                        if pages is not None:
                            page_result['status'] = 'got'
                            page_result['pages'] = pages
                            page_result['proxies'] = proxies
                            return page_result
                        else:
                            page_result['status'] = 'nofind'
                    else:
                        page_result['status'] = 'nofind'
                else:
                    page_result['status'] = 'nofind'
                return page_result
        except:
            pass

def get_ids(session, cookies, fullname):
        ids = []
        ids_result = {'status':None,'ids':ids,'proxies':None}
        page_result = get_pages(session, cookies, fullname)
        status = page_result['status']
        if status == 'nocode' or status == 'nopage':
            ids_result['status'] = 'wrong'
            return ids_result

        elif status == "nofind":
            ids_result['status'] = 'noid'
            return ids_result

        else:
            pages = int(page_result['pages'])

            proxy = page_result['proxies']
            for page in range(1, pages+1):
                res = 0
                while True:
                    res += 1
                    if res > 10:
                        ids_result['status'] = 'wrong'
                        return ids_result
                    if res > 1:
                        proxy = None

                    print("page:%s to get ids"%page)
                    code = get_verify_code(session,cookies)
                    if code is None:
                        ids_result['status'] = 'wrong'
                        return ids_result
                    time.sleep(2)

                    # 搜索
                    try:
                        unitname = fullname.encode('gb2312')
                        search_url = "http://www.miitbeian.gov.cn/icp/publish/query/icpMemoInfo_searchExecute.action"

                        payload = {
                            "certType": "-1",
                            "jumpPageNo":'',
                            "mainLicense": "",
                            "mainUnitCertNo": "",
                            "mainUnitNature": "-1",
                            "page.pageSize":20,
                            "pageNo":page,
                            "siteDomain": '',
                            "siteIp": "",
                            "siteName": "",
                            "siteUrl": "",
                            "unitName": unitname,
                            "verifyCode": code
                        }
                        if proxy is not None:
                            proxies = proxy
                        else:
                            proxies = get_proxy('http')

                        r = session.post(search_url, data=payload, headers=headers, cookies=cookies, proxies=proxies,timeout=10)
                        content = r.text

                        if content.find('备案信息查询') >= 0:
                            if content.find('没有符合条件的记录') == -1:
                                d = pq(html.fromstring(content))
                                infos = d('table').eq(1).find('tr')
                                for info in infos:
                                    if pq(info).find('span.hui') >= 0:
                                        result = util.re_get_result(r"doDetail\('(.*?)'\)",pq(info).html())
                                        if result is not None:
                                            _id, = result
                                            ids.append(_id)
                                break
                            else:
                                print('该 fullname 未备案...')
                                ids_result['status'] = 'noid'
                                return ids_result
                    except:
                        pass
            ids_result['status'] = 'got'
            ids_result['ids'] = ids
            ids_result['proxies'] = proxies
            return ids_result

def fetch_by_id(session,cookies,_id,proxy):
    content_result = {'status':None,'content':None}
    print('%s to get content'%_id)
    res = 0
    while True:
        # 获取详细验证码
        res += 1
        if res > 20:
            content_result['status'] = 'wrong'
            return content_result
        if res > 1:
            proxy = None

        if proxy is not None:
            proxies = proxy
        else:
            proxies = get_proxy('http')

        try:
            get_detail_verify_code_url = "http://www.miitbeian.gov.cn/getDetailVerifyCode?%s" % random.randint(0,100)
            r = session.get(get_detail_verify_code_url, headers=headers, cookies=cookies,proxies=proxies,timeout=10)
            i = Image.open(StringIO.StringIO(r.content))
            img_path = "vfimg/test1.png"
            i.save(img_path)

            # OCR
            _, code = captcha_miit.process(img_path)
            code = code.lower()
            print("code=%s"%code)
            if check_code(code, 4) is False:
                continue

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
            r = session.post(detail_url, data=payload, headers=headers, cookies=cookies,proxies = proxies,timeout=10)
            content = r.text
            if "验证码错误，请重新输入" in content:
                continue
            print("%s sucess to get content"%_id)
            content_result = {'status': 'got', 'content': content}
            return content_result
        except:
            pass

def get_items(content):
    processflag = False
    global ITEMS
    d = pq(html.fromstring(content.decode("utf-8", "ignore")))
    tb1 = d("body> table").eq(0).find('tr').eq(1).find('td').eq(1).find('table')
    tb2 = d("body> table ").eq(1).find('tr').eq(1).find('td').eq(1).find('table')


    mainBeianhao = None
    beianDate = None
    organizer = None
    organizertype = None
    websitename = None
    homepage = None
    domain = None
    beianhao = None

    if tb1.html() is not None and tb2.html() is not  None :
        if tb1.html().find('备案') >= 0 and tb2.html().find('备案') >= 0:
            if tb1.find('tr').eq(0).find('td').eq(0).text().strip() == "备案/许可证号：":
                mainBeianhao = tb1.find('tr').eq(0).find('td').eq(1).text().strip()
            if tb1.find('tr').eq(0).find('td').eq(2).text().strip() == "审核通过时间：":
                beianDate = tb1.find('tr').eq(0).find('td').eq(3).text().strip()
            if tb1.find('tr').eq(1).find('td').eq(0).text().strip() == "主办单位名称：":
                organizer = tb1.find('tr').eq(1).find('td').eq(1).text().strip()
            if tb1.find('tr').eq(1).find('td').eq(2).text().strip() == "主办单位性质：":
                organizertype = tb1.find('tr').eq(1).find('td').eq(3).text().strip()
            if tb2.find('tr').eq(0).find('td').eq(0).text().strip() == "网站名称：":
                websitename = tb2.find('tr').eq(0).find('td').eq(1).text().strip()
            if tb2.find('tr').eq(2).find('td').eq(0).text().strip() == "网站备案/许可证号：":
                beianhao = tb2.find('tr').eq(2).find('td').eq(1).text().strip()
            homepages = []
            if tb2.find('tr').eq(0).find('td').eq(2).text().strip() == "网站首页网址：":
                divs = tb2.find('tr').eq(0).find('td').eq(3).find('div')
                for div in divs:
                    homepages.append(pq(div).find('a').text().strip())
            if tb2.find('tr').eq(1).find('td').eq(2).text().strip() == "网站域名：":
                domains = tb2.find('tr').eq(1).find('td').eq(3).find('div')
                for d in domains:
                    domain = pq(d).text()
                    for h in homepages:
                        if h.find(domain) >=0:
                            homepage = h
                        else:
                            homepage = "www." + domain
                    item = {
                            "domain": domain,
                            "organizer": organizer,
                            "organizerType": organizertype,
                            "beianhao": beianhao,
                            "mainBeianhao": mainBeianhao,
                            "websiteName": websitename,
                            "homepage": homepage,
                            "beianDate": beianDate,
                                }
                    print(json.dumps(item, ensure_ascii=False, indent=2))
                    if item not in ITEMS:
                        ITEMS.append(item)
                    processflag = True
    return processflag

def run(fullname,maxretry):
    retry = 0
    while True:
        retry +=1
        if retry > maxretry:
            retry_count = get_count('retry')
            if retry_count is not None:
                save("retry",retry_count+1)
            return
        result_cookies = get_cookie()
        if result_cookies['status'] == 'wrong':
            continue
        cookies = result_cookies['cookies']
        global B
        B += 1
        save('B',B)
        session = requests.Session()
        time.sleep(2)
        ids_result = get_ids(session,cookies,fullname)
        status = ids_result['status']
        if status == 'noid':
            global E
            E += 1
            save('E',E)
            return
        elif status == "wrong":
            continue
        else:
            ids = ids_result['ids']
            idsnews = list(set(ids))
            proxies = ids_result['proxies']

            fidflag = False
            for _id in idsnews:
                content_result = fetch_by_id(session, cookies, _id,proxies)
                status = content_result['status']
                if status == "wrong":
                    continue
                content = content_result['content']
                flag = get_items(content)
                if flag is True:
                    fidflag = True
            if fidflag is True:
                # global E
                E += 1
                save('E',E)
                return
            else:
                pass

def save(name,value):
    mongo = db.connect_mongo()
    collection = mongo.raw.count
    item = collection.find_one({'count':'fullname'})
    if item.has_key(name):
        collection.update({'count': 'fullname'}, {"$set": {name:value}})
    mongo.close()

def get_count(item):
    count = 'fullname'
    mongo = db.connect_mongo()
    collection_count = mongo.raw.count
    if collection_count.find_one({'count': count}) is not None:
        count_item = collection_count.find_one({'count': count})
        mongo.close()
        if item == 'alpha':
            return count_item["A"],count_item["B"],count_item["C"],count_item["D"],count_item["E"],
        elif item == 'retry':
            return count_item['retry']
    mongo.close()
    return None


def _prepare():
    os.system("rm -rf output/ vfimg/")
    os.system("mkdir output vfimg")

def main(fullname):
    count_item = get_count('alpha')
    if count_item is  None :
        print('mongo error!!!')
        return []
    global A,B,C,D,E
    # 计数参数
    (A, B, C, D, E) = count_item
    global ITEMS
    # 存放 item
    ITEMS = []
    # global A
    A += 1
    save('A',A)

    maxretry = 5
    # __clear_brs()
    _prepare()
    run(fullname,maxretry)
    # __clear_brs()
    print(" A:%s \n B:%s \n C:%s \n D:%s \n E:%s \n"%(A,B,C,D,E))
    print("总共获取到%s条数据"%len(ITEMS))
    return ITEMS

if __name__ == '__main__':
    main("北京云杉世纪网络科技有限公司")





