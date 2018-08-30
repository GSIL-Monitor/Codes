# -*- coding: utf-8 -*-
import  sys,os

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import mongodb_util, mysql_util

def check_funding_gongshang(keyWord,investorIds):
    gongshang_companies=[]  #[{code,id,name}]
    for company in  mongodb_util.get_companyFullname_by_gongshang(keyWord):
        fullName = company['name']
        companies = mysql_util.get_company_by_fullName(fullName)
        for i in companies:
            if i not in gongshang_companies:gongshang_companies.append(i)

    funding_companies=[]
    if not isinstance(investorIds, list):investorIds=[investorIds]
    for investorId in investorIds:
        for company in mysql_util.get_company_by_funding_investor(investorId):
            if company not in funding_companies: funding_companies.append(company)

    cnt=0
    result=[]
    for company in gongshang_companies:
        if company not in funding_companies:
            # print 'code:%s,name:%s,companyId:%s,'%(company['code'],company['name'],company['companyId'])
            result.append(company['companyId'])
            cnt+=1

    # print 'gongshang_companies has %s, funding_companies has %s'%( len(gongshang_companies),len(funding_companies))
    # print cnt
    return result

# return companyid list
if __name__ == "__main__":
    check_funding_gongshang('戈壁',149)
