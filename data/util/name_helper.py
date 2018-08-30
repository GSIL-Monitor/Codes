#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-
import util
import hz
import db
import re
import urllib

def name_check(unicode_name):
    chinese = hz.is_chinese_string(unicode_name)
    company = None
    if chinese:
        company = False
        if unicode_name.find(u"公司") > 0:
            company = True
        elif unicode_name.find(u"企业") > 0:
            company = True
        elif unicode_name.find(u"中心") > 0:
            company = True
        elif unicode_name.find(u"事务所") > 0:
            company = True
        elif unicode_name.find(u"研究院") > 0:
            company = True
        elif unicode_name.find(u"会社") > 0:
            company = True
        elif unicode_name.find(u"合伙") > 0:
            company = True
        elif unicode_name.endswith(u"所") > 0:
            company = True
        elif unicode_name.endswith(u"部") > 0:
            company = True
        elif unicode_name.endswith(u"会") > 0:
            company = True
        elif unicode_name.endswith(u"院") > 0:
            company = True
        elif unicode_name.endswith(u"社") > 0:
            company = True
        elif unicode_name.endswith(u"店") > 0:
            company = True
        elif unicode_name.endswith(u"馆") > 0:
            company = True
        elif unicode_name.endswith(u"室") > 0:
            company = True
        elif unicode_name.endswith(u"厂") > 0:
            company = True
        elif unicode_name.endswith(u"楼") > 0:
            company = True
    return chinese, company

def english_name_check(unicode_name):
    chinese = hz.is_chinese_string(unicode_name)
    english = False
    company = None
    if not chinese:
        english = True
        company = False
        n = unicode_name.strip().lower()
        if n.endswith("ltd") or \
            n.endswith("ltd.") or \
            n.endswith("inc") or \
            n.endswith("inc.") or \
            n.endswith("llc") or \
            n.endswith("llc.") or \
            n.endswith("limited") or \
            n.endswith("corporation") or \
            n.endswith("company"):
            company = True

    return english, company


def company_name_normalize(unicode_name):
    if unicode_name is None:
        return None
    chinese, company = name_check(unicode_name)
    if chinese is False:
        return unicode_name

    name = unicode_name.strip().replace("(", u"（").replace(")", u"）").replace(" ","").replace(u"\u3000","")
    #print name
    new_name = ""
    for c in name:
        if hz.is_chinese(c) or ord(c) > 0xfee0 or hz.is_number(c) or hz.is_alphabet(c):
            new_name += c
    return new_name


def get_main_company_name(unicode_name):
    if unicode_name.find(u"公司") == -1:
        return unicode_name
    main_name = unicode_name.split(u"公司")[0] + u"公司"
    return main_name


def get_location_from_company_name(unicode_name):
    #上海测试公司
    #测试（上海）公司
    #北京测试上海分公司
    conn = db.connect_torndb()
    locations = list(conn.query("select locationName from location"))
    conn.close()
    m_location = None
    sub_location = None
    for location in locations:
        if unicode_name.startswith(location["locationName"]):
            m_location = location["locationName"]
            break

    if m_location is None:
        r = util.re_get_result(u"（(.*)）",unicode_name)
        if r is not None:
            location, = r
            conn = db.connect_torndb()
            l = conn.query("select * from location where locationName=%s", location)
            conn.close()
            if l is not None:
                m_location = location

    r = util.re_get_result(u"(.*)分公司",unicode_name)
    if r is not None:
        name, = r
        for location in locations:
            if name.endswith(location["locationName"]):
                sub_location = location["locationName"]
                break
    return m_location, sub_location


def get_short_name(unicode_name):
    name = unicode_name.strip()
    if name.find(u"－") > 0:
        name = name.split(u"－")[0].strip()
    if name.find(u"—") > 0:
        name = name.split(u"—")[0].strip()
    if name.find(u"-") > 0:
        name = name.split(u"-")[0].strip()
    if hz.is_chinese_string(name):
        if name.find(u" ") > 0:
            name = name.split(u" ")[0].strip()
    if name.find(u"|") > 0:
        name = name.split(u"|")[0].strip()
    if name.find(u"·") > 0:
        name = name.split(u"·")[0].strip()

    return name

def position_check(unicode_name):
    type = 5030
    n = unicode_name.strip().lower()
    if n.find(u"离职") >= 0:
        type = 5040
    elif n.find(u"创始") >= 0 or \
         n.find(u"合伙人") >= 0 or \
         re.search(r"founder", n, re.I):
        type = 5010
    elif n.find(u"总监") >= 0 or \
        n.find(u"总裁") >= 0 or \
        n.find(u"总经理") >= 0 or \
        n.find(u"董事") >= 0 or \
        n.find(u"首席") >= 0 or \
        n.find(u"校长") >= 0 or \
        n.find(u"法人") >= 0 or \
        re.search(r"c\wo", n, re.I):
        type = 5020
    return type

def crunchbase_position_check(unicode_name):
    type = 5030
    n = unicode_name.strip().lower()
    if n.find('ceo') >= 0 or \
       n.find('chief executive officer') >= 0 or \
       re.search(r"founder", n, re.I) or \
       re.search(r'chairman',n,re.I):
        type = 5010
    elif n.find('chief') >= 0 or \
         n.find('officer') >= 0 or \
         n.find('president') >= 0 or \
         n.find('manager') >= 0 or \
         n.find('engineer') >= 0 or \
         n.find('director') >= 0 or \
         re.search(r'vp',n,re.I)  or \
         re.search(r"c\wo", n, re.I):
        type = 5020
    return type


if __name__ == '__main__':
    print urllib.quote("Guangzhou Hui Zheng financial consulting co., LTD")
    print urllib.quote("市场与销售CMO")
    print company_name_normalize(u"Guangzhou Hui Zheng financial consulting co., LTD")
    print position_check(u"市场与销售CMO")
    '''
    print position_check(u"阿道夫总经理")
    print position_check(u"阿道夫总计")
    print position_check(u"阿道夫cdo")
    print position_check(u"阿FOUNDER")
    print company_name_normalize("上海技术(测试)公司abc".decode("utf-8"))
    print name_check("上海技术公司".decode('utf-8'))
    print name_check("abc asdfa".decode("utf-8"))

    print get_location_from_company_name(u"上海测试公司")
    print get_location_from_company_name(u"测试（上海）公司")
    print get_location_from_company_name(u"北京测试上海分公司")

    print get_short_name(u"每日星座运程 · NowNow 闹闹的女巫店 HD")
    print get_short_name(u"聊吧—-美女帅哥·私密聊天·交友约会")
    print get_short_name(u"每日开眼 Eyepetizer -  精选视频推荐，每天大开眼界")
    print get_short_name(u"IT")
    print get_short_name(u"旅神－去日本旅游美食购物打折一手掌握")
    print get_short_name(u"旅游门户-客户端")

    print get_main_company_name(u"东易日盛家居装饰集团股份有限公司A6L子公司")
    print get_main_company_name(u"中国新闻社唐印科技发展有限公司")

    print english_name_check(u"Shenzhen Beabow Software Technology Co., Ltd.")
    print english_name_check(u"Shenzhen Beabow Software Technology Co.")
    '''