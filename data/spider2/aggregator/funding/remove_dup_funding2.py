# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

#logger
loghelper.init_logger("remove_empty_funding", stream=True)
logger = loghelper.get_logger("remove_empty_funding")

scores = {"investment":1, "round":1, "currency":1}

def create_fundDateDict(fundings):
    fdDict = {}
    for funding in fundings:
        if funding["fundingDate"] is not None:fdDict.setdefault(str(funding["fundingDate"].year)+str(funding["fundingDate"].month),[]).append(funding)
    return fdDict

def get_investors(fundingId):
    conn = db.connect_torndb()
    rels = conn.query("select * from funding_investor_rel where (active is null or active='Y') and fundingId=%s order by investorId", fundingId)
    investorIds = [int(rel["investorId"]) for rel in rels]
    conn.close()
    return investorIds

def remove_by_sameMonth(companyId, code):
    conn = db.connect_torndb()
    fundings_all = conn.query("select * from funding where companyId=%s and (active is null or active='Y')", companyId)
    # conn.close()
    fdDict = create_fundDateDict(fundings_all)
    fundings_check = [funding for funding in fundings_all if funding.has_key("createUser") and funding["createUser"] is None]
    if len(fundings_check) == 0 :
        # logger.info("Company: %s|%s fundings are all dealed by people or None\n", code, companyId)
        return []
    deleteIds = []; checkedMonth = []
    for fundC in fundings_check:
        if fundC["fundingDate"] is None or fundC["id"] in deleteIds:continue
        if len(fdDict[str(fundC["fundingDate"].year)+str(fundC["fundingDate"].month)]) < 2: continue
        if str(fundC["fundingDate"].year)+str(fundC["fundingDate"].month) in checkedMonth: continue
        checkedMonth.append(str(fundC["fundingDate"].year)+str(fundC["fundingDate"].month))
        fundscore = {}; maxscroe = 0; remainIds = []; maxscroeId=None; maxround=None
        for fund in fdDict[str(fundC["fundingDate"].year)+str(fundC["fundingDate"].month)]:
            if fund["createUser"] is not None:
                score = 10
                remainIds.append(fund["id"])
            else:
                score = len([column for column in scores if fund[column] is not None and str(fund[column]).strip() != "" and str(fund[column]).strip() != "0"])
                if len(get_investors(fund["id"])) > 0: score += 1
            fundscore[fund["id"]] = score
            if maxscroe < score:
                maxscroe = score
                maxscroeId = fund["id"]
                maxround = fund["round"]
            if maxscroe == score and fund["round"] is not None and (maxround is None or fund["round"]> maxround):
                maxscroeId = fund["id"]
                maxround = fund["round"]
        for id in fundscore:
            # logger.info("%s,%s",id,fundscore[id])
            if id not in remainIds and id != maxscroeId and id not in deleteIds: deleteIds.append(id)
    conn.close()
    return deleteIds

def combine_investors(targetFundid, fundings):
    conn = db.connect_torndb()
    tagetInvestors = get_investors(targetFundid)
    for fund in fundings:
        if fund["id"] == targetFundid: continue
        rels = conn.query("select * from funding_investor_rel where (active is null or active='Y') and fundingId=%s order by investorId",fund["id"])
        for rel in rels:
            if rel["investorId"] is not None and int(rel["investorId"]) not in tagetInvestors:
                conn.update("update funding_investor_rel set fundingId=%s where id=%s", targetFundid, rel["id"])
                logger.info("Update funding_rel: %s with %s <-> %s", rel["id"], fund["id"], targetFundid)
            else:
                # # conn.execute("delete from funding_investor_rel where id=%s", rel["id"])
                conn.update("update funding_investor_rel set active=%s where id=%s", 'N', rel["id"])
                logger.info("Remove funding_rel: %s since dup", rel["id"])
    conn.close()



def select_remain_fundings(fundings):
    remainFundIds = [funding["id"] for funding in fundings if funding.has_key("createUser") and funding["createUser"] is not None]
    if len(remainFundIds) == 0:
        maxscroe = 0; maxscroeId=None
        for fund in fundings:
            score = len([column for column in scores if fund[column] is not None and str(fund[column]).strip() != "" and str(fund[column]).strip() != "0"])
            if len(get_investors(fund["id"]))> 0: score += 1
            if maxscroe < score:
                maxscroe = score
                maxscroeId = fund["id"]
        combine_investors(maxscroeId, fundings)
        remainFundIds.append(maxscroeId)
    return remainFundIds


def compare_select(companyId, code, funding, compare_fundings,column, update_deleteIds):
    same_fundings = []
    deids = []
    # if len(update_deleteIds)>0: logger.info("Update deleteids: %s",update_deleteIds)
    for cfund in compare_fundings:
        if cfund["id"] in update_deleteIds: continue
        if funding["id"] == cfund["id"]: continue
        if column in ["investment", "fundingDate"] and (cfund[column] is None or funding[column] is None): continue
        if column == "fundingDate" and (cfund[column]-funding[column]).days > -20 and (cfund[column]-funding[column]).days< 20:
            logger.info("Company %s|%s has Funding Date Same for %s/%s/%s/%s and %s/%s/%s/%s", companyId, code, funding["id"],funding["fundingDate"],
                        funding["investment"],funding["round"],cfund["id"],cfund["fundingDate"],cfund["investment"],cfund["round"])
            same_fundings.append(cfund)
        elif column == "investment" and funding[column]> 0 and cfund[column] == funding[column] and cfund["precise"] == funding["precise"] and cfund["currency"] == funding["currency"]:
            logger.info("Company %s|%s has Funding Investment Same for %s/%s/%s/%s and %s/%s/%s/%s", companyId, code, funding["id"],funding["fundingDate"],
                        funding["investment"],funding["round"],cfund["id"],cfund["fundingDate"],cfund["investment"],cfund["round"])
            same_fundings.append(cfund)
        elif column == "investor" and get_investors(funding["id"]) == get_investors(cfund["id"]):
            logger.info("Company %s|%s has Funding Investor Same for %s/%s/%s/%s and %s/%s/%s/%s", companyId, code, funding["id"],funding["fundingDate"],
                        funding["investment"],funding["round"],cfund["id"],cfund["fundingDate"],cfund["investment"],cfund["round"])
            same_fundings.append(cfund)
        # else:return_fundings.append(cfund)
    if len(same_fundings)>0:
        same_fundings.append(funding)
        remainIds = select_remain_fundings(same_fundings)
        for sf in same_fundings:
            if sf["id"] not in update_deleteIds and sf["id"] not in remainIds: deids.append(sf["id"])
    return deids

def remove_by_1010(companyId, code):
    conn = db.connect_torndb()
    fundings_all = conn.query("select * from funding where companyId=%s and (active is null or active='Y') and (round=1010 or round=1011)", companyId)
    fundings_check = [funding for funding in fundings_all if funding.has_key("createUser") and funding["createUser"] is None]
    if len(fundings_check) == 0:
        # logger.info("Company: %s|%s fundings are all dealed by people or None\n", code, companyId)
        return []
    deleteIds = []
    # logger.info("Checking %s|%s fundings", companyId, code)
    for fundC in fundings_check:
        for colum in ["fundingDate", "investment", "investor"]:
            if fundC["id"] in deleteIds: continue
            new_deleteIds = compare_select(companyId, code, fundC, fundings_all, colum, deleteIds)
            if len(new_deleteIds) > 0:deleteIds.extend(new_deleteIds)
            # if len(deleteIds)>0: logger.info(deleteIds)
    conn.close()
    return deleteIds

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cids = conn.query("select companyId,count(*) from funding where (active is null or active='Y') group by companyId having count(*)>1")
    num = 0
    tot = len(cids)
    deleteids= []
    for cid in cids:
        company = conn.get("select * from company where (active is null or active='Y') and id=%s", cid["companyId"])
        # 摩拜单车,ofo
        if company is None or int(cid["companyId"]) in [131894, 13371]:continue
        # dids = remove_by_sameMonth(company["id"], company["code"])
        dids = remove_by_1010(company["id"], company["code"])
        if len(dids) > 0:
            logger.info("Delete company %s, %s fundings:", company["id"], company["code"])
            for id in dids:
                num += 1
                fundD = conn.get("select * from funding where id=%s and createUser is null", id)
                if fundD is None:
                    logger.info("Something wrong!******************************************")
                    continue
                logger.info("***********FundId:%s, %s/%s/%s", fundD["id"],fundD["fundingDate"],fundD["investment"],fundD["round"])
                deleteids.append(id)
                #delete funding
                # conn.execute("delete from funding_investor_rel where fundingId=%s", id)
                conn.update("update funding_investor_rel set active=%s where fundingId=%s", 'N', id)
                # conn.execute("delete from funding where id=%s", id)
                conn.update("update funding set active=%s where id=%s", 'N', id)
            logger.info("")
    logger.info(num)
    logger.info(len(deleteids))
    logger.info(deleteids)
    conn.close()
