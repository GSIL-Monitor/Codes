# -*- coding: utf-8 -*-
#funding中investors未关联的内容，如果能匹配到投资机构的工商注册名称，则替换短名，并记录funding_investor_rel
#注意一个机构多个基金投资的情况，要去重

import os, sys
import json, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("funding_investor_structuring", stream=True)
logger = loghelper.get_logger("funding_investor_structuring")


def process():
    id = -1
    conn = db.connect_torndb()
    fullnames = conn.query("select a.investorId,a.name,i.website,i.name as shortname from investor_alias a "
                           " join investor i on a.investorId=i.id"
                           " where a.type=12010 "
                           " and (a.active is null or a.active='Y')"
                           " and (i.active is null or i.active='Y')"
                           " and a.verify='Y'")
    while True:
        fs = conn.query("select * from funding where id>%s order by id limit 1000", id)
        if len(fs) == 0:
            break
        for f in fs:
            funding_id = f["id"]
            if funding_id > id:
                id = funding_id
            str_investors = f["investors"]
            if str_investors is None or str_investors == "":
                continue
            logger.info(str_investors)
            investors = json.loads(str_investors.replace("\n",","))

            _investors = []
            flag = False
            for s in investors:
                if s["type"] == "text":
                    text = s["text"]
                    if len(text) < 4:
                        _investors.append(s)
                        continue
                    if contain_company_name(text) is False:
                        _investors.append(s)
                        continue
                    names = find_all_investor_fullnames(fullnames, text)
                    if len(names) > 0:
                        #logger.info(text)
                        #logger.info(names)
                        result = structure(text, names)
                        result = remove_dup(result)
                        #logger.info(result)
                        #logger.info("")
                        _investors.extend(result)
                        flag = True
                    else:
                        _investors.append(s)
                else:
                    _investors.append(s)

            if flag:
                logger.info(str_investors)
                _str_investors =json.dumps(_investors, ensure_ascii=False)
                logger.info(_str_investors)
                _str_raw_investors = gen_raw_str(_investors)
                logger.info(_str_raw_investors)
                logger.info("")
                corp = conn.get("select * from company where id=%s",f["companyId"])
                logger.info("companyId: %s, companyName: %s", corp["id"], corp["name"])
                conn.execute("set autocommit=0")
                for inv in _investors:
                    if inv["type"] == "investor":
                        rel = conn.get("select * from funding_investor_rel"
                                       " where (active is null or active='Y')"
                                       " and fundingId=%s and investorId=%s",
                                       funding_id, inv["id"])
                        if rel is None:
                            logger.info("insert rel: %s", inv["text"])
                            conn.insert("insert funding_investor_rel(fundingId,investorId,createUser,verify,active,createTime) values(%s,%s,139,'Y','Y',now())",
                                        funding_id, inv["id"])
                conn.update("update funding set investorsRaw=%s, investors=%s where id=%s",
                            _str_raw_investors, _str_investors, funding_id)
                conn.execute("commit")
                # exit()

    conn.close()


def gen_raw_str(result):
    str = ""
    for item in result:
        str += item["text"]
    return str


def remove_dup(result):
    _result = []
    investorids = {}
    for item in result:
        if item["type"] == "text":
            _result.append(item)
        else:
            if not investorids.has_key(item["id"]):
                investorids[item["id"]] = 1
                _result.append(item)
    last = _result[-1]
    if last["type"] == "text" and (last["text"].strip()=="" or
                                           last["text"].strip()=="，" or
                                           last["text"].strip()=="," or
                                           last["text"].strip() == "、"
                                   ):
        _result.pop(-1)
    return _result


def find_first_one(text, names):
    index = 65536
    first = None
    for name in names:
        i = text.find(name["name"])
        if i>=0 and i<index:
            index = i
            first = name
    return first, index


def structure(text, names):
    results = []

    name, index = find_first_one(text, names)
    if name is None:
        if text.strip() != "":
            results.append({
                "type":"text",
                "text":text
            })
        return results

    if index > 0:
        results.append({
            "type": "text",
            "text": text[:index]
        })
    results.append({
        "type": "investor",
        "text": name["shortname"],
        "id": name["investorId"],
        "link": name["website"],
    })
    text = text[(index+len(name["name"])):]
    results.extend(structure(text,names))
    return results

def contain_company_name(text):
    if u"公司" in text or u"合伙" in text or u"基金" in text:
        return True
    return False


def find_all_investor_fullnames(fullnames, text):
    names = []
    while True:
        f = find_investor_fullname(fullnames, text)
        if f is None:
            break
        else:
            names.append(f)
            text = text.replace(f["name"], "")
    return names


def find_investor_fullname(fullnames, text):
    for f in fullnames:
        if f["name"] in text:
            return f
    return None


if __name__ == "__main__":
    while True:
        logger.info("Start...")
        process()
        logger.info("End.")
        time.sleep(10*60)