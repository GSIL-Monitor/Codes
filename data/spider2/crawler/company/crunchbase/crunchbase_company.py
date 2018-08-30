# -*- coding: utf-8 -*-
import os, sys, datetime
import random
import requests, json
from selenium import webdriver
# # from selenium.webdriver.common.proxy import Proxy, ProxyType
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import db
#
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import proxy_pool

# sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../test'))
# # import chrome_test


TYPE = 36001
SOURCE = 13130
URLS = []
Cookie = ''
Proxiesr = []
Rule = {'type':'HTTPS', 'anonymous':'high'}
Rule2 = {'type':'https', 'anonymity':'high'}


def get_proxy():
    global Proxiesr
    if len(Proxiesr) == 0:
        Proxiesr = proxy_pool.get_single_proxy_x(Rule,1000)
    while True:
        try:
            # item = proxy_pool.get_single_proxy(Rule)
            item = Proxiesr[random.randint(0, len(Proxiesr) - 1)]
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            print('%s:%s' % (ip, port))
            url = "https://www.baidu.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 30
            proxies = {
                'https': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('hao123') >= 0:
                print('ip:%s for crunchbase' % ip_port)
                return ip, port
        except Exception,e:
            print('Proxy Exception:%s' % e)

def get_proxy2():
    while True:
        try:
            item = proxy_pool.get_single_proxy(Rule2)
            ip, port = item['ip'], item['port']
            ip_port = ip + ':' + str(port)
            print('%s:%s' % (ip, port))
            url = "https://www.baidu.com/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }
            timeout = 10
            proxies = {
                'https': ip_port
            }
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if r.text.find('hao123') >= 0:
                print('ip:%s for crunchbase' % ip_port)
                return ip, port
        except Exception, e:
            print('Proxy Exception:%s' % e)

def delete_tmpfile():
    command = 'rm -f /tmp/tmpaddon*'
    os.system(command)
    print('clean tmp_file done')

def get_cookie():
    global Cookie, IP, PORT
    print('to get cookie...')
    i = 1
    while Cookie == '':
        delete_tmpfile()
        if i >= 3 :
            IP, PORT = get_proxy2()
            i = 0
        bro = None
        try:
            options = webdriver.FirefoxOptions()
            options.binary_location = '/root/firefox/firefox'
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument(
                'User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36')
            options.add_argument('Accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            profile = webdriver.FirefoxProfile()
            profile.set_preference('network.proxy.type', 1)
            # profile.set_preference('network.proxy.http', '120.52.73.1')
            # profile.set_preference('network.proxy.http_port', 96)  # int
            profile.set_preference('network.proxy.ssl', IP)
            profile.set_preference('network.proxy.ssl_port', int(PORT))
            profile.update_preferences()

            bro = webdriver.Firefox(firefox_profile=profile,firefox_options=options,executable_path='./geckodriver')
            # bro = webdriver.Firefox(firefox_options=options,executable_path='./geckodriver')
            bro.implicitly_wait(120)
            # 设置超时
            bro.set_page_load_timeout(120)
            bro.set_script_timeout(120)
            print ("here go website")
            bro.get('https://www.crunchbase.com')
            print ("here go website 1")
            time.sleep(60)
            print ("here go website 2")

            cookie = [item["name"] + "=" + item["value"] for item in bro.get_cookies()]
            if cookie is not None:
                cookiestr = ';'.join(item for item in cookie)
                print('cookie:',cookiestr)
                if cookiestr.find('D_HID') >= 0 or cookiestr.find('_ok') >= 0 or cookiestr.find('__cfduid') >= 0:
                    print(cookiestr)
                    Cookie = cookiestr
                    bro.quit()
                    time.sleep(5)
                    # __clear_brs()
                    return Cookie
                else:
                    bro.quit()
                    # __clear_brs()
                    print('fail to get cookie...')
            bro.quit()
            time.sleep(5)

        except Exception, e:
            if bro is not None:
                print ("here close website")
                bro.close()
                bro.quit()

            # __clear_brs()
            print(e)
            i += 1
            time.sleep(5)

def make_payload(collection_id, company_name=None, time=None, querys={}):
    payload = {}
    query = ''
    if collection_id == 'organization.companies':
        if querys['field_id'] == 'funding':
            query = [{"type": "predicate", "field_id": "last_funding_at", "operator_id": "between", "values": ["a day ago","today"]}]
        elif querys['field_id'] == 'announced':
            query = [{"type": "sub_query", "collection_id": "acquisition.was_acquired.forward", "query": [
                {'field_id': 'announced_on', 'operator_id': 'between', 'type': 'predicate', 'values': ['a day ago','today']}]}]
        payload = {
            "field_ids": ["identifier", "categories", "location_identifiers", "short_description", "rank_org_company"],
            "order": [{"field_id": "rank_org_company", "sort": querys['sort']}],
            "query": query,
            "field_aggregators": [],
            "collection_id": collection_id,
            "limit": 15
        }

    elif collection_id == 'funding_rounds':
        payload = {
            "field_ids": ["identifier", "funded_organization_identifier", "investment_type", "money_raised", "announced_on"],
            "order": [],
            "query": [{'field_id':'announced_on','operator_id':'eq','type':'predicate','values':[querys['value']]}],
            "field_aggregators": [],
            "collection_id": collection_id,
            "limit": 15
        }

    postdata = json.dumps(payload)
    return postdata

def crawler_news(properties):
    global Cookie, IP, PORT
    i = 0
    j = 0
    while True:
        while i >= 3 :
            IP, PORT = get_proxy2()
            i = 0

        proxies = {
            'https':'%s:%d'%(IP,PORT)
        }

        company = {}
        name = properties['name']
        uuid = properties['uuid']
        permalink = properties['permalink']
        print('start crawler %s|%s' % (name, uuid))
        cookie = Cookie
        headers = {'Cookie': '%s' % cookie,
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0'}
        url = 'https://www.crunchbase.com/v4/data/entities/organizations/{}?field_ids=["identifier","layout_id","facet_ids","title","short_description","is_locked"]&layout_mode=view'.format(
            permalink)

        try:
            result = requests.get(url, headers=headers, proxies=proxies,timeout=30)
            time.sleep(2)
            content = result.text

            if content.find('properties') >= 0:
                print('success to get %s msg' % name)

                try:
                    j_comp = json.loads(content)
                    j_cards = j_comp['cards']

                except:
                    print('wrong content not json')
                    return



                company_base = company['company_base'] = {}
                member = company['member'] = {}
                past_finance = company['past_finance'] = {}
                product = company['product'] = {}
                events = company['events'] = {}

                logo = None
                if properties['logo_id'] is not None:
                    logo = properties['logo_id']
                company_base['logo'] = logo
                tags = None
                if properties['categories'] is not None:
                    tags = properties['categories']
                company_base['tags'] = tags

                company_base['overview_funding'] = {}
                if j_cards.has_key('overview_headline'):
                    company_base['overview_funding'] = j_cards['overview_headline']
                company_base['properties'] = j_comp['properties']
                company_base['num_exits'] = j_cards['exits_headline']
                company_base['locations'] = j_cards['overview_image_description']
                company_base['overview_fields'] = j_cards['overview_fields']
                company_base['overview_fields2'] = j_cards['overview_fields2']
                company_base['overview_school_fields'] = j_cards['overview_school_fields']
                company_base['num_overview_investor'] = j_cards['overview_investor_fields']
                company_base['company_type'] = j_cards['overview_company_fields']
                company_base['description'] = j_cards['overview_description']
                company_base['twitter'] = j_cards['twitter']

                member['current_advisors'] = j_cards['current_advisors_image_list']  # 董事会成员 投资者
                member['num_current_advisors'] = j_cards['advisors_headline']
                member['past_employees'] = j_cards.get('past_employees_image_list')
                member['num_past_employees'] = j_cards['past_employees_headline']
                member['current_employees'] = j_cards['current_employees_image_list']
                member['num_current_employees'] = j_cards['current_employees_headline']

                past_finance['acquired_by_fields'] = j_cards['acquired_by_fields']
                past_finance['funds'] = j_cards['funds_list']
                past_finance['acquisitions'] = j_cards['acquisitions_list']
                past_finance['num_acquisitions'] = j_cards['acquisitions_headline']
                past_finance['num_investments'] = j_cards['investments_headline']
                past_finance['investments'] = j_cards['investments_list']
                past_finance['num_investors'] = j_cards['investors_headline']
                past_finance['investors'] = j_cards['investors_list']
                past_finance['exits_company'] = j_cards['exits_image_list']
                past_finance['funding_rounds'] = j_cards['funding_rounds_list']
                past_finance['funding_total'] = j_cards['funding_rounds_headline']
                past_finance['funds_headline'] = j_cards['funds_headline']
                past_finance['ipo_fields'] = j_cards['ipo_fields']

                product['num_sub_organizations'] = j_cards['sub_organizations_headline']
                product['sub_organizations'] = j_cards['sub_organizations_image_list']

                events['event_appearances'] = j_cards['event_appearances_list']
                events['num_event_appearances'] = j_cards['event_appearances_headline']
                # print(json.dumps(company, ensure_ascii=False,indent=4))
                acquired = past_finance['acquired_by_fields']
                funding = past_finance['funding_rounds']
                if acquired is not None or len(funding) > 0:
                    save(SOURCE, TYPE, url, uuid, name, company)
                else:
                    print('no funding msg!')
                return

            else:
                # print(content)
                print 'fail to crawl %s'% name
                i = 3
                j += 1
                print('bad detail content times:%d'%j)

        except Exception as e:
            print 'requests or mongo error:%s'%e
            i += 1
        if j >= 3:
            return

def save(SOURCE, TYPE, url, key, name, content):
    print("Saving: %s"% url)

    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": TYPE,
        "url": url,
        "key": key,
        "name": name,
        "content": content,
        "count":0
    }

    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": key})
    if item is not None :
        try:
            if item.has_key('count') is False:
                collection.update({"source": SOURCE, "type": TYPE, "key": key},{"$set":{"count":0,'date':datetime.datetime.now()}})
                item['count'] = 0
            if item["content"] != content and item['count'] == 0:
                collection.update({"source": SOURCE, "type": TYPE, "key": key},{"$set":{"content":content,"count":1,'date':datetime.datetime.now()}})
                print("old data changed for company: %s"%key)
            else:
                if item['count'] == 0:
                    print("old data not changed for company: %s"%key)
                    collection.update({"source": SOURCE, "type": TYPE, "key": key},{"$set": {"count": 1,'date':datetime.datetime.now()}})
                else:
                    print("count = 1,do nothing")
        except Exception as e:
            print('mongo error:%s!'%e)
    else:
        try:
            collection.insert_one(collection_content)
        except:
            print('mongo error!')
    mongo.close()
    print("Saved: %s"%url)

def run_news(collection):
    # print(json.dumps(ids, ensure_ascii=False,indent=4))
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        logo_id = None
        categories = None
        if collection == 'organization.companies':
            identifier = URL['identifier']
            if identifier.get('image_id', None):
                logo_id = identifier['image_id']

            if URL.get('categories', None):
                categories = URL['categories']

        else:
            identifier = URL['funded_organization_identifier']
            if identifier.get('image_id', None):
                logo_id = identifier['image_id']

        uuid = identifier['uuid']
        name = identifier['value']
        permalink = identifier['permalink']

        properties = {
            'uuid': uuid,
            'name': name,
            'permalink':permalink ,
            'logo_id': logo_id,
            "categories": categories,
        }

        crawler_news(properties)

def process(content,collection):
    try:
        j = json.loads(content)
    except:
        print('wrong content not json')
        return None

    companies = j['entities']
    print('count：%s' % len(companies))
    cnt = 0
    if len(companies) == 0:
        return cnt, cnt
    for a in companies:
        try:

            name = a['properties']['identifier']['value']
            uuid = a['properties']['identifier']['uuid']
            if collection == 'funding_rounds':
                name = a['properties']['funded_organization_identifier']['value']
                uuid = a['properties']['funded_organization_identifier']['uuid']


            # pname = a['properties']['identifier']['permalink']
            print('company:%s|%s'%(name, uuid))

            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "key": uuid,'count':1})
            mongo.close()
            if item is None:
                URLS.append(a['properties'])
        except Exception as e:
            print(e)
            print("cannot get company data")
    return len(companies), len(URLS)

def run():
    global Cookie, IP, PORT
    while True:
        Cookie = get_cookie()
        collections = ['organization.companies','funding_rounds']
        # collections = ['funding_rounds']
        # # collections = ['organization.companies']
        last = 0
        for collection in collections:
            url = 'https://www.crunchbase.com/v4/data/searches/%s'%collection
            queryss = [{'value':'today'},{'value':'yesterday'}]
            if collection == 'organization.companies':
                queryss = [{'field_id': 'funding', 'sort': 'asc'},{'field_id': 'funding', 'sort': 'desc'},{'field_id': 'announced', 'sort': 'asc'},{'field_id': 'announced', 'sort': 'desc'}]
            for querys in queryss:
                exits = 1
                postdata1 = make_payload(collection,querys=querys)
                headers = {'Cookie': '%s' % Cookie,
                           'Content-Type': 'application/json',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0'}

                # 每周一周二 爬取上周四五的收购情况
                weekday = time.strftime("%A", time.localtime(time.time()))
                postdata2 = None

                if weekday == 'Monday' or weekday == 'Tuesday':
                    postdata2 = {
                                "field_ids": ["identifier", "categories", "location_identifiers", "short_description", "rank_org_company"],
                                "order": [{"field_id": "rank_org_company", "sort": 'asc'}],
                                "query": [{"type": "sub_query", "collection_id": "acquisition.was_acquired.forward", "query": [
                                          {'field_id': 'announced_on', 'operator_id': 'between', 'type': 'predicate', 'values': ['last thursday','last friday']}]}] ,
                                "field_aggregators": [],
                                "collection_id": 'organization.companies',
                                "limit": 15}
                    postdata2 = json.dumps(postdata2)
                postdatas = []
                if postdata2 is not None and last == 0:
                    print("to get last weenkend acquisition ")
                    postdatas.append(postdata2)
                    postdatas.append(postdata1)
                    last = 1
                else:
                    postdatas.append(postdata1)

                for postdata in postdatas:
                    print(datetime.datetime.now())
                    i = 0
                    j = 0
                    while True:
                        if i >= 3:
                            IP, PORT = get_proxy2()
                            i = 0
                        proxies = {
                            'https':'%s:%d'%(IP,int(PORT))
                        }
                        try:
                            result = requests.post(url, headers=headers, data=postdata, proxies=proxies,timeout=30)
                            content = result.text
                            if content.find('count') >= 0:
                                try:
                                    cnt, cnt2 = process(content,collection)
                                    if cnt2 > 0:
                                        print("%s has %s/%s fresh company" % (url, cnt2, cnt))
                                        run_news(collection)
                                    else:
                                        print("no fresh company")
                                    if  collection == 'funding_rounds' and querys == queryss[-1]:
                                        return
                                    break
                                except Exception, ex:
                                    print('something wrong at process or run_news:%s'%ex)
                                    raise ValueError('something wrong at process or run_news')
                            else:
                                # print(content)
                                print('bad content')
                                i = 3
                                j += 1
                                print('bad content times:%d'%j)

                        except Exception as e:
                            print('requests error:%s'%e)
                            i += 1
                            continue
                        if j >= 5:
                            raise ValueError('bad content')

def start_run(flag):
    while True:
        # global Proxiesr
        # Proxiesr = proxy_pool.get_single_proxy_x(Rule, 1000)
        global IP, PORT
        IP, PORT = get_proxy2()
        print("%s company all %s start..."%(SOURCE, flag))
        print(datetime.datetime.now())
        run()
        if flag == "incr":
            print("%s company all %s end..."%(SOURCE, flag))
            time.sleep(60 * 60 * 2 )
        else:
            return

def __clear_brs():

    for line in os.popen('ps -ef |grep firefox').readlines():
        vars = line.split()
        proc = ''.join(vars[7:])  # get proc description
        if line.find('/root/firefox') == -1: continue
        pid = vars[1]  # get pid
        ppd = vars[2]
        out = os.popen('kill ' + pid)
        out2 = os.popen('kill ' + ppd)
    print('clear firefox done')


if __name__ == '__main__':
    print('gogogo')
    param = 'incr'
    start_run(param)
