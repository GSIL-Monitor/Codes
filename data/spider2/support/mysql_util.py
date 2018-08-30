# -*- coding: utf-8 -*-
import  sys,os

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db

def get_funding_by_company(companyName):
    conn = db.connect_torndb()
    fundings = conn.query('''select f.* from company c join funding f on c.id=f.companyId where c.name=%s ''',companyName)
    conn.close()
    if len(fundings) > 0:
        return fundings
        # return [int(location["locationId"]) for location in locations]
    else:
        return []

def get_company_by_funding_investor(investorId):
    conn = db.connect_torndb()
    results = conn.query('''select distinct f.companyId,c.name,c.code
    from funding_investor_rel fi
    join funding f on f.id=fi.fundingId and (f.active='Y' or f.active is null )
    join company c on c.id=f.companyId and (c.active='Y' or c.active is null )
    where (fi.active='Y' or fi.active is null )
    and fi.investorId=%s ''',investorId)
    conn.close()
    if len(results) > 0:
        return results
    else:
        return []

def get_company_by_fullName(fullName):
    conn = db.connect_torndb()
    results = conn.query('''select distinct ca.companyId,c.name,c.code from company_alias ca
    join company c on c.id=ca.companyid and (c.active='Y' or c.active is null )
    where (ca.active='Y' or ca.active is null )
    and (ca.name=%s or c.fullName=%s or c.name=%s)  ''', fullName,fullName,fullName)
    conn.close()
    if len(results) > 0:
        return results
    else:
        return []


if __name__ == "__main__":
    # print get_funding_by_company(u'全州印象')
    # print get_company_by_funding_investor(149)
    print get_company_by_fullName('北京百车宝科技有限公司')

