# -*- coding: utf-8 -*-
import os, sys, time
import datetime
import json
import urllib2
from pyquery import PyQuery as pq
from StringIO import StringIO
import gzip
from lxml import html

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
# import loghelper
import url_helper
import name_helper
import util


# sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/website'))
# import website

# sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/beian'))
# import icp_chinaz
# import beian_links

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/beian_icp'))
# import icp_beian_query_by_domain
import icp_beian_query_by_fullname

# #logger
# loghelper.init_logger("beian_expand", stream=True)
# logger = loghelper.get_logger("beian_expand")

def get_meta_info(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
    headers = {'User-Agent': user_agent,
               'accept-language':'zh-CN,zh;q=0.8,en;q=0.6',
               'Accept-Encoding':'gzip'}
    try:
        request = urllib2.Request(url, None, headers)
    except:
        return None
    opener = urllib2.build_opener()
    retries = 0
    while True:
        try:
            r = opener.open(request, timeout=17)
            if r.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(r.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else:
                data = r.read()
            content = util.html_encode(data)
            redirect_url = url_helper.url_normalize(r.geturl())
            #logger.info(redirect_url)
            #logger.info(content)
            d = pq(html.fromstring(content))
            title = d("title").text()
            #logger.info(title)
            keywords = d("meta[name='keywords']").attr("content")
            if keywords is None:
                keywords = d("meta[name='Keywords']").attr("content")
            #logger.info(keywords)
            description = d("meta[name='description']").attr("content")
            if description is None:
                description = d("meta[name='Description']").attr("content")
            #logger.info(description)

            flag, domain = url_helper.get_domain(url)
            if flag is not True:
                domain = None
            return {
                "url": url,
                "redirect_url": redirect_url,
                "domain": domain,
                "title": title,
                "tags": keywords,
                "description": description,
                "httpcode": 200
            }
            # break
        except:
            retries += 1
        if retries >= 3:
            return None
    # return None

def save_collection_beian(items):
    mongo = db.connect_mongo()
    collection_name = mongo.info.beian
    for item in items:
        try:
            #logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))
            # beian 是即时更新 即便查询domain存在 以新得到的beian为准进行更新
            if collection_name.find_one({"domain": item["domain"]}) is not None:
                collection_name.delete_one({"domain": item["domain"]})
            item["createTime"] = datetime.datetime.now()
            item["modifyTime"] = item["createTime"]
            # logger.info("insert new *****************domain :%s", item["domain"])
            print ("insert new *****************domain :%s"% item["domain"])
            collection_name.insert_one(item)
        except Exception as e:
            print ("mongo error: %s"%e)
            continue
    mongo.close()
    print("save beian msgs to mongo done...")

def saveWebsite(item):
    mongo = db.connect_mongo()
    collection_website = mongo.info.website
    # in case that related websites have been saved before
    # website 只针对 url查询 没有查询到的 才进行插入
    record = collection_website.find_one({"url": item["url"]})
    if record is None:
        item["createTime"] = datetime.datetime.now()
        item["modifyTime"] = item["createTime"]
        try:
            id = collection_website.insert(item)
        except:
            return None
    mongo.close()
    print("save website to mongo done...")

def checkwebsite(items):
    nitems = []
    # 我们会把好的网站存到mysql.artifact里，但是所有网站都会存到mongo.info.website里面
    for item in items:
        mongo = db.connect_mongo()
        collection_website = mongo.info.website
        URL = "http://www." + item["domain"]
        meta = collection_website.find_one({"url": URL})
        mongo.close()
        if meta is None:
            print("Checking : %s"% URL)
            meta = get_meta_info(URL)
        if meta is None :
            meta = {
                "url": URL,
                "httpcode": 404
            }
            saveWebsite(meta)
            # 404 代表不能访问，不存到mysql.artifact
        else:
            saveWebsite(meta)

            if meta.has_key("httpcode") and meta["httpcode"] == 200:
                bflag = True
                # 校验黄赌毒
                for bbword in ["赌博","一夜情","裸聊","三级片","色情","葡京","床戏","AV","黄色"]:
                    if meta.has_key("description") is True and meta["description"] is not None and meta["description"].find(bbword) >= 0:
                        bflag = False
                        break
                    if meta.has_key("title") is True and meta["title"] is not None and meta["title"].find(bbword) >= 0:
                        bflag = False
                        break
                    if meta.has_key("tags") is True and meta["tags"] is not None and meta["tags"].find(bbword) >= 0:
                        bflag = False
                        break
                #黄赌毒网站也不存到mysql.artifact
                if bflag is True:
                    nitems.append(item)
    return nitems

def save_beian_artifacts(items, companyId):
    conn = db.connect_torndb()
    for item in items:
        try:
            homepage = "http://www." + item["domain"]

            artifact = conn.get("select * from artifact where type=4010 and companyId=%s and link=%s limit 1",
                                           companyId, homepage)
            if artifact is None:
                artifact = conn.get("select * from artifact where type=4010 and companyId=%s and domain=%s limit 1",
                    companyId, item["domain"])

            type = 4010
            if artifact is None:
                print ("here insert *********************************")
                sql = "insert artifact(companyId, name, link, type, domain, createTime,modifyTime,createUser) \
                                  values(%s,%s,%s,%s,%s,now(),now(),%s)"
                conn.insert(sql, companyId, item["websiteName"], homepage, type, item["domain"],-570)
        except Exception as e:
            print("mysql error :%s"%e)
            continue
    conn.close()
    print("save beian artifacts to mysql done...")

def get_count(count):
    mongo = db.connect_mongo()
    collection_count = mongo.raw.count
    if collection_count.find_one({'count':count}) is not None:
        count_item = collection_count.find_one({'count':count})
        mongo.close()
        return count_item
    mongo.close()
    return None

def _reset():
    mongo = db.connect_mongo()
    collection = mongo.raw.count
    try:
        collection.update({'count':'fullname'},{"$set":{'A':0,'B':0,'C':0,'D':0,'E':0}})
    except Exception as e:
        print("mongo error: %s"%e)
    mongo.close()

def save_error(name,value):
    mongo = db.connect_mongo()
    collection = mongo.raw.count
    item = collection.find_one({'count':'fullname'})
    if item.has_key(name):
        try:
            collection.update({'count': 'fullname'}, {"$set": {name:value}})
        except Exception as e:
            print("mongo error: %s" % e)
    mongo.close()

if __name__ == '__main__':

    id = 0 #todo
    _reset()
    while True:
        # id = 60071
        conn = db.connect_torndb()
        corporates = conn.query("select * from corporate where (active is null or active='Y') and verify='Y' and id>%s limit 1000"%(id))
        for corporate in corporates:
            id = corporate["id"]
            # corporate 对应 companies， 一个corporate可能对应多个产品线companies
            companies = conn.query("select * from company where (active is null or active='Y') and corporateId=%s"%corporate["id"])
            # logger.info(json.dumps(companies,ensure_ascii=False,cls=util.CJsonEncoder,indent=2))
            print ("corporate_id:%s"%corporate['id'])
            fullname = corporate['fullName']
            if fullname == '' or fullname is None:
                continue
            print (fullname)

            # 根据fullName进行备案信息查询，返回list 包含该公司名下所有的网站的备案信息
            beians = icp_beian_query_by_fullname.main(fullname)
            count_item = get_count('fullname')
            if count_item is None or  (count_item.has_key('A') and count_item.has_key('E') and count_item['A'] != count_item['E']):
                print ('A:%s--->E:%s'%(count_item['A'],count_item['E']))
                print("something error!----->corporate_id:%s"%corporate['id'])
                # 将错误状况写入mongo，以便查看
                item_error = 1
                if count_item.has_key('error'):
                    item_error = count_item['error']+1
                save_error('error',item_error)
                _reset()
                continue
            if len(beians) == 0:
                continue

            # logger.info(json.dumps(beians,ensure_ascii=False,cls=util.CJsonEncoder,indent=2))
            """use info  db.beian.find().sort({createTime:-1}).limit(num)"""
            save_collection_beian(beians)


            # 针对得到的所有网站进行清洗，一：判断是否可以访问，HTTP 200？ 二：判断是否是黄色网站，并返回清洗后的结果
            """use info db.website.find().sort({createTime:-1}).limit(num)"""
            rel_websites = checkwebsite(beians)
            # logger.info(rel_websites)


            for company in companies:
                # 保存得到的网站到Mysql.artifact中，保存过程中检查是否已经有了，含有的（包含被删除的）都不会保存
                """ select * from artifact order by createTime desc limit 0,num \G;"""
                save_beian_artifacts(rel_websites, company["id"])
            # id += 1
        # 是否全部corporates都检查过了
        if len(corporates) == 0:
            time.sleep(60 * 60)
            print ('sleep a while...')
            id = 0
            _reset()










