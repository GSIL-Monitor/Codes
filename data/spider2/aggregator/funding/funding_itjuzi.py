# -*- coding: utf-8 -*-

import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import helper

#logger
loghelper.init_logger("remove_empty_funding", stream=True)
logger = loghelper.get_logger("remove_empty_funding")


def remove_13030_funding():
    conn = db.connect_torndb()
    fs = conn.query("select * from source_funding where sourceCompanyId in (select id from source_company where source=13030)")
    for f in fs:
        conn.execute("delete from source_funding_investor_rel where sourceFundingId=%s", f["id"])
        conn.execute("delete from source_funding where id=%s",f["id"])
    conn.close()

def set_processed(source_fundings):
    conn = db.connect_torndb()
    for s_f in source_fundings:
        conn.update("update source_funding set processStatus=2 where id=%s", s_f["id"])
    conn.close()

def aggregate1(sf,company_id, test=False):
    flag = True

    table_names = helper.get_table_names(test)

    conn = db.connect_torndb()
    sfirs = conn.query("select * from source_funding_investor_rel where sourceFundingId=%s", sf["id"])
    if sf["investment"] == 0 and len(sfirs)==0:
        conn.close()
        return True

    f = conn.get("select * from " + table_names["funding"] + " where companyId=%s and round=%s and (active is null or active!='N') limit 1",
                 company_id, sf["round"])
    if f is not None:
        logger.info("find here1")
    if f is None and sf["fundingDate"] is not None and sf["round"]<=1020:
        '''
        f = conn.get("select * from " + table_names["funding"] + " where companyId=%s and year(fundingDate)=%s and month(fundingDate)=%s and (active is null or active!='N') limit 1",
                 company_id, sf["fundingDate"].year, sf["fundingDate"].month)
        '''
        f = conn.get("select * from funding where companyId=%s and fundingDate>date_sub(%s,interval 1 month) and fundingDate<date_add(%s,interval 1 month) and (active is null or active!='N') limit 1",
                company_id, sf["fundingDate"], sf["fundingDate"])
        if f is not None:
            logger.info("find here2")
    if f is None:
        logger.info("insert")
        sql = "insert " + table_names["funding"] + "(companyId,preMoney,postMoney,investment,\
                    round,roundDesc,currency,precise,fundingDate,fundingType,\
                    active,createTime,modifyTime,createUser) \
                values(%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,'Y',now(),now(),%s)"
        fundingId=conn.insert(sql,
                              company_id,
                              sf["preMoney"],
                              sf["postMoney"],
                              sf["investment"],
                              sf["round"],
                              sf["roundDesc"],
                              sf["currency"],
                              sf["precise"],
                              sf["fundingDate"],
                              8030,
                              -2
                              )

    else:
        fundingId = f["id"]
        if f["round"] == 1110 and sf["round"] == 1105:
            conn.update("update " + table_names["funding"] + " set round=1105 where id=%s",fundingId)

    if f and f["createUser"] is not None:
        pass
    else:
        for sfir in sfirs:
            investor_id = None
            investor_company_id = None

            if sfir["investorType"] == 38001:
                source_investor = conn.get("select * from source_investor where id=%s", sfir["sourceInvestorId"])
                if source_investor is None:
                    flag = False
                    continue
                investor_id = source_investor["investorId"]
                if investor_id is None:
                    flag = False
                    continue
                investor  = conn.get("select * from investor where id=%s", investor_id)
                if investor is None or investor["active"] == 'N':
                    flag = False
                    continue
            else:
                source_company = conn.get("select * from source_company where id=%s", sfir["sourceCompanyId"])
                if source_company is None or source_company["companyId"] is None:
                    flag = False
                    continue
                investor_company_id = source_company["companyId"]

            if sfir["investorType"] == 38001:
                funding_investor_rel = conn.get("select * from " + table_names["funding_investor_rel"] + " \
                                where investorId=%s and fundingId=%s limit 1",
                                investor_id, fundingId)
            else:
                funding_investor_rel = conn.get("select * from " + table_names["funding_investor_rel"] + " \
                                where companyId=%s and fundingId=%s limit 1",
                                investor_company_id, fundingId)

            if funding_investor_rel is None:
                sql = "insert " + table_names["funding_investor_rel"] + "(fundingId, investorType, investorId, companyId, currency, investment,\
                        precise,active,createTime,modifyTime,createUser) \
                        values(%s,%s,%s,%s,%s,%s,%s,'Y',now(),now(),%s)"
                conn.insert(sql,
                            fundingId,
                            sfir["investorType"],
                            investor_id,
                            investor_company_id,
                            sfir["currency"],
                            sfir["investment"],
                            sfir["precise"],
                            -2
                        )

    # update company stage
    if not test:
        funding = conn.get("select * from funding where companyId=%s order by round desc, fundingDate desc limit 1",
                           company_id)
        if funding is not None:
            conn.update("update company set round=%s, roundDesc=%s where id=%s",
                        funding["round"],funding["roundDesc"],company_id)

    conn.close()

    return flag


if __name__ == '__main__':
    logger.info("Begin...")
    # remove_13030_funding()
    # logger.info("funding aggregator start")
    conn = db.connect_torndb()
    # deleteIds = []
    (n1, n2, n3, n4, n5, n6, n7) = (0, 0, 0, 0, 0, 0, 0)
    # cs = conn.query("select * from company where (active is null or active='Y') order by id")
    cs = [210408]
    for cc in cs:
        n6 += 1


        # scs = conn.query("select * from source_company where source=13030 and (active is null or active='Y') order by id")

        sfs = conn.query("select * from source_funding where sourceCompanyId in (select id from \
                         source_company where (active is null or active='Y') and source=13030 and companyId=%s)", cc)
        # logger.info(sfs)

        fundings_all = conn.query("select * from funding where companyId=%s and (active is null or active='Y')", cc)
        fundings_check = [funding for funding in fundings_all if funding.has_key("createUser") and funding["createUser"] is not None]
        if len(fundings_all) > 0:
            # logger.info("Company: %s|%s fundings are  by people or None\n", company["code"], company["id"])
            n3 += 1
            # set_processed(sfs)
            continue

        # n5 += 1
        # deleting all funding data.
        # for funding_all in fundings_all:
        #     deleteIds.append(funding_all["id"])
        #     conn.update("update funding_investor_rel set active=%s, modifyUser=%s where fundingId=%s", 'N', -1, funding_all["id"])
        #     conn.update("update funding set active=%s, modifyUser=%s where id=%s", 'N', -1, funding_all["id"])
        if len(sfs) > 0:
            n1 += 1
            flag = True
            for sf in sfs:
                logger.info(sf)
                flag = aggregate1(sf, cc)
                if flag is False:
                    break
            if flag is True:
                n5 += 1
                logger.info("New funding added for company : %s", cc)
                set_processed(sfs)
            else:
                logger.info("Something wrong with aggregating funding for company : %s|%s", c["code"], c["id"])
                n4 += 1
                #set_processed(sfs)
            pass

    logger.info("funding aggregator end.")
    logger.info("%s/%s/%s/%s/%s/%s", n1, n2, n3, n4, n5, n6)
    # logger.info(len(deleteIds))
    # time.sleep(30 * 60)
    #fullfill for 1
    # mn=0; mn1=0
    # modi_funds = conn.query("select * from funding where modifyUser=-1 and investorsRaw is not null")
    # for mf in modi_funds:
    #     mn += 1
    #     conn.update("update funding_investor_rel set active=%s, modifyUser=%s where fundingId=%s", 'Y', 220 ,mf["id"])
    #     conn.update("update funding set active=%s, modifyUser=%s where id=%s", 'Y', 220, mf["id"])
    #     if mf["round"] is not None:
    #         mmf = conn.get("select * from funding where companyId=%s and createUser=-2 and round=%s", mf["companyId"], mf["round"])
    #         # logger.info("mf: %s/%s map %s created by -2", mf["companyId"],mf["round"], )
    #         if mmf is not None:
    #             conn.update("update funding_investor_rel set active=%s, modifyUser=%s where fundingId=%s", 'N', 220, mmf["id"])
    #             conn.update("update funding set active=%s, modifyUser=%s where id=%s", 'N', 220, mmf["id"])
    #             mn1 +=1
    # logger.info("%s/%s", mn1,mn)
    #fullfill for 2
    # funding_ids = [424,425,2026,6485,6486,6487,7447,7874,9247,32165,32166,33858,34469,41883,41916,41936,41947,41948,41949,41982,42130,42231,42235,42319,42320,42321,42412,42413,42436,42448,42464,42468,42469,42470,42486,42526,42535,42536,42537,42582,42605,42678,42712,42715,42739,42825,42826,42828,43033,43036,43147,43148,43149,43441,43472,43515,43516,43517,43619,43620,43621,43829,43830,43831,43832,44001,44039,44040,44066,44173,44194,44195,44197,44198,44201,44246,44261,44262,44346,44347,44348,44349,44406,44429,44517,44670,44743,44747,44877,45074,45462,45608,45653,45654,45751,45833,45888,45929,45930,45932,45934,46225,46286,46287,46451,46473,46567,46603,46675,46676,46790,47005,47098,47117,47463,47487,47488,47628,47629,47630,47801,48028,48122,48123,48145,48268,48363,48439,48601,48867,49091,49165,49170,49173,49174,49246,49406,49524,49571,49677,49767,49825,49826,49881,49896,49914,49915,50026,50086,50087,50171,50259,50343,50406,50569,50718,50724,51005,51006,51086,51087,51340,51341,51342,51419,51584,51585,51595,51670,51695,51697,51706,51707,51709,51776,51794,51840,51841,51865,51866,51918,52003,52004,52028,52030,52032,52034,52075,52138,52139,52262,52276,52285,52286,52447,52581,52627,52675,52772,52900,52941,52942,52995,53008,53009,53010,53049,53081,53082,53106,53138,53157,53223,53246,53264,53265,53409,53410,53411,53412,53488,53609,53690,53692,53833,53899,54066,54070,54074,54133,54191,54208,54209,54228,54229,54256,54338,54353,54360,54439,54440,54481,54508,54662,54663,54754,54777,54806,54807,54828,54878,54882,54904,54948,54953,54964,54969,55043,55140,55157,55185,55198,55247,55294,55393,55493,55494,55505,55506,55690,55691,55844,55887,56020,56127,56231,56239,56396,56409,56410,56411,56457,56458,56533,56566,56704,56723,56736,56744,57008,57009,57962,58030,58222,58310,58311,58739,58822,58827,58977,59150,59151,59243,59354,59456,59620,59764,59765,59767,59817,59818,59903,60298,60324,60884,61172,61388,61389,61456,62137,62138,62203,62516,63137,63156,63288,63289,63334,63506,63528,63636,63801,63802,63894,63933,63972,64002,64110,64152,64483,64491,64628,64659,65237,65240,65260,65446,65509,65554,65608,65656,65725,66112,66147,66162,66206,66236,66302,66327,66341,66424,66487,66585,66710,66741,66753,66759,66785,66786,66840,67010,67011,67018,67029,67030,67031,67032,67033,67034,67524,67537,67544,67604,67606,67607,67608,67609,67610,67679,67682,67986,68093,68198,68221,68222,68321,68390,68542,68543,68550,68554,68740,68741,68742,68746,68842,68843,68856,68884,68903,68915,68916,68917,68923,68941,68957,69039,69124,69152,69154,69294,69295,69325,69331,69356,69400,69415,69444,69470,69629,69686,69720,69725,69742,69772,69923,69956,69977,70065,70082,70194,70206,70208,70209,70274,70369,70381,70399,70520,70529,70651,70721,70833,70919,70920,70980,71029,71076,71171,71238,71244,71338,71382,71399,71473,71474,71476,71487,71514,71785,71787,71967,72100,72115,72132,72220,72581,72700,72723,72734,72746,72753,72834,72905,72906,72925,72929,72930,72943,73017,73021,73041,73044,73046,73068,73096,73139,73150,73203,73330,73383,73449,73517,73560,73581,73645,73678,73728,73893,73902,73923,74090,74143,74200,74291,74341,74395,74481,74542,74584,74616,74669,74730,74746,74781,74859,74896,74940,74949,74972,75010,75061,75095,75098,75101,75110,75123,75153,75199,75202,75214,75276,75514,75826,75889,76115,76344,76492,76558,76667,76696,76708,76729,76733,76739,76763,76767,76795,76863,76881,76894,76904,76919,76949,76978,76992,77007,77010,77079,77109,77126,77128,77130,77186,77202,77205,77207,77257,77263,77315,77325,77436,77494,77516,77521,77523,77546,77547,77563,77572,77573,77581,77591,77594,77617,77623,77627,77628,77674,77733,77744,77780,77793,77803,77826,77876,77897,77911,77933,77961,78043,78072,78084,78088,78089,78090,78091,78092,78093,78104,78109,78139,78155,78159,78161,78163,78168,78304]
    # n=0;n1=0;n2=0;n3=0
    # for id in funding_ids:
    #     f0 = conn.get("select * from funding where id=%s", id)
    #     if f0 is not None: n +=1
    #     f = conn.get("select * from funding where active='N' and id=%s",id)
    #     if f is not None:
    #         n1+=1
    #         if f["modifyUser"] == -1: n2+=1
    #         if f["round"] is not None:
    #             mmfs = conn.query("select * from funding where companyId=%s and createUser=-2 and round=%s", f["companyId"],f["round"])
    #             logger.info("mf: %s/%s map %s created by -2", f["companyId"],f["round"], len(mmfs))
    #             if len(mmfs)==1:
    #                 n3+=1
    #                 conn.update("update funding_investor_rel set active=%s, modifyUser=%s where fundingId=%s", 'Y', 220,f["id"])
    #                 conn.update("update funding set active=%s, modifyUser=%s where id=%s", 'Y', 220, f["id"])
    #                 conn.update("update funding_investor_rel set active=%s, modifyUser=%s where fundingId=%s", 'N', 220, mmfs[0]["id"])
    #                 conn.update("update funding set active=%s, modifyUser=%s where id=%s", 'N', 220, mmfs[0]["id"])
    #
    # for id in [77186]:
    #     conn.update("update funding_investor_rel set active=%s, modifyUser=%s where fundingId=%s", 'Y', 220, id)
    #     conn.update("update funding set active=%s, modifyUser=%s where id=%s", 'Y', 220, id)
    # for id in []:
    #     conn.update("update funding_investor_rel set active=%s, modifyUser=%s where fundingId=%s", 'N', 220,id)
    #     conn.update("update funding set active=%s, modifyUser=%s where id=%s", 'N', 220, id)
    # logger.info("%s/%s/%s/%s",n1,n2,n3,n)
    conn.close()
    logger.info("End.")