# -*- coding: utf-8 -*-
import os, sys
import pandas as pd

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, name_helper

#logger
loghelper.init_logger("stats", stream=True)
logger = loghelper.get_logger("stats")

rounds = [
    (0, u"轮次不明"),
    (1010,u"种子轮"),
    (1011,u"天使轮"),
    (1020,u"Pre-A"),
    (1030,u"A"),
    (1031,u"A+"),
    (1039,u"Pre-B"),
    (1040,u"B"),
    (1041,u"B+"),
    (1050,u"C"),
    (1051,u"C+"),
    (1060,u"D"),
    (1070,u"E"),
    (1080,u"F"),
    (1090,u"late stage"),
    (1100,u"Pre-IPO"),
    (1105,u"新三板"),
    (1106,u"新三板定增"),
    (1110,u"IPO"),
    (1111,u"Post-IPO"),
    (1120,u"收购"),
    (1130,u"战略投资"),
    (1131,u"战略合并"),
    (1140,u"私有化"),
    (1150,u"债权融资"),
    (1160,u"股权转让"),
]

def main():
    data = {}

    #
    # total
    sql = """select f.round round, count(*) cnt from funding f 
join company c on f.companyId=c.id 
join corporate cp on cp.id=c.corporateId 
where (f.active is null or f.active='Y') 
and (c.active is null or c.active='Y') 
and cp.locationId<371 
and (
(publishDate is not null and publishDate>='2017/1/1' and publishDate<'2017/12/1')
or
(publishDate is null and fundingDate>='2017/1/1' and fundingDate<'2017/12/1')
) 
group by round order by round;"""
    items = conn.query(sql)
    for item in items:
        data[item["round"]] = {"total": item["cnt"]}

    # sector
    sectors = list(conn.query("select * from sector where level=1 and active='Y' order by id"))
    for sector in sectors:
        sql = """
        select f.round round, count(*) cnt from funding f 
join company c on f.companyId=c.id 
join corporate cp on cp.id=c.corporateId 
join company_tag_rel r on c.id=r.companyId
where (f.active is null or f.active='Y') 
and (c.active is null or c.active='Y')  
and (r.active is null or r.active='Y')
and cp.locationId<371 
and (
(publishDate is not null and publishDate>='2017/1/1' and publishDate<'2017/12/1')
or
(publishDate is null and fundingDate>='2017/1/1' and fundingDate<'2017/12/1')
) 
and r.tagId=%s
group by round order by round;
        """
        # logger.info("tagId=%s", sector["tagId"])
        items = conn.query(sql, sector["tagId"])
        for item in items:
            data[item["round"]][sector["sectorName"]] = item["cnt"]

    # print
    result = {}
    result["round"] = []
    result["total"] = []
    for sector in sectors:
        result[sector["sectorName"]] = []

    logger.info("round,total,%s", ",".join([sector["sectorName"] for sector in sectors]))
    for round, round_name in rounds:
        result["round"].append(round_name)
        # logger.info(round)
        item = data.get(round)
        total = 0
        if item is not None:
            total = item.get("total", 0)
        result["total"].append(total)

        cnts = []
        for sector in sectors:
            cnt = 0
            if item is not None:
                cnt = item.get(sector["sectorName"], 0)
            # logger.info("%s: %s", sector["sectorName"], cnt)
            cnts.append(str(cnt))
            result[sector["sectorName"]].append(cnt)
        logger.info("%s,%s,%s", round_name, total, ",".join(cnts))

    df = pd.DataFrame(result)
    columns=["round", "total"]
    for sector in sectors:
        columns.append(sector["sectorName"])

    df.to_excel('logs/2017.xlsx', index=False, columns=columns)


if __name__ == "__main__":
    conn = db.connect_torndb()
    main()