# -*- coding: utf-8 -*-
import os, sys
import find_company
import company_aggregator
import company_info_expand
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util
import helper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/beian'))
import icp_chinaz
import beian_links

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler/screenshot'))
import screenshot_website


#logger
loghelper.init_logger("check_company_aggregator", stream=True)
logger = loghelper.get_logger("check_company_aggregator")

def clean_test_tables(test):
    conn = db.connect_torndb()
    conn.execute("delete from test_company_member_rel where id>0")
    conn.execute("delete from test_funding_investor_rel where id>0")
    conn.execute("delete from test_member where id>0")
    conn.execute("delete from test_funding where id>0")
    conn.execute("delete from test_company_alias where id>0")
    conn.execute("delete from test_artifact where id>0")
    conn.execute("delete from test_company where id>0")

    conn.close()

if __name__ == '__main__':
    conn = db.connect_torndb()
    companies = list(conn.query("select id from company where (active is null or active='Y') order by id desc"))
    conn.close()
    test = True

    # init crawler
    beian_links_crawler = beian_links.BeianLinksCrawler()
    icp_chinaz_crawler = icp_chinaz.IcpchinazCrawler()
    screenshot_crawler = screenshot_website.phantomjsScreenshot()
    wrong ={}
    num = 0
    cnum = 0
    for company in companies:
        cnum += 1
        company_id = company["id"]
        conn = db.connect_torndb()
        scs = list(conn.query("select * from source_company where (active is null or active='Y') and (source is not null and source != 13002 and (source < 13100 or source >= 13110)) and companyStatus!=2020 and companyId=%s order by id", company_id))
        if len(scs) > 1:
            conn = db.connect_torndb()
            #delete from test tables;
            clean_test_tables(test)
            #re-do aggregator for each source_company:
            ids =[]
            for sc in scs:
                company_info_expand.expand_source_company(sc["id"],beian_links_crawler, icp_chinaz_crawler, screenshot_crawler, test=True)
                ids.append(str(sc["id"]))
            logger.info("Company: %s has %s source companies: %s", company_id, len(scs), ",".join(ids))

            round_max= len(scs)
            round = 0

            sc0 = scs.pop(0)
            logger.info("Insert New company with source company: %s", sc0["id"])
            company_aggregator.aggregator(sc0, test=True)

            while True:
                round += 1
                logger.info("********************round %s", round)
                scs_new = []
                for sc in scs:

                    companyid = find_company.find_company(sc,test=True)
                    logger.info("source_company_id: %s matched company_id=%s", sc["id"], companyid)

                    if companyid is not None:
                        company_aggregator.aggregator(sc, test=True)
                    else:
                        scs_new.append(sc)

                if len(scs_new) > 0:
                    if round > round_max -1:

                        sc_ids_wrong = [str(sc["id"]) for sc in scs_new if sc.has_key("id")]
                        sc_ids_right = [str(id) for id in ids if id not in sc_ids_wrong]
                        logger.info("*****************Wrong aggregation with company: %s:  %s can not match other %s  (%s)", company["id"], ",".join(sc_ids_wrong), ",".join(sc_ids_right), ",".join(ids))
                        num += 1
                        logger.info("*****************Total number of wrong aggregation: %s / %s", num, cnum)
                        wrong[company["id"]] ="("+",".join(sc_ids_right)+"  +  "+",".join(sc_ids_wrong)+")"
                        break
                    else:
                        #continue loop for check
                        scs = scs_new
                else:
                    logger.info("**************Right aggregation with company: %s", company["id"])
                    logger.info("*****************Total number of wrong aggregation: %s / %s", num, cnum)
                    break
    logger.info("wrong company:")
    for company in wrong:
        logger.info("%s->%s", company, wrong[company])
    logger.info("*****************Total number of wrong aggregation: %s / %s", num, cnum)

