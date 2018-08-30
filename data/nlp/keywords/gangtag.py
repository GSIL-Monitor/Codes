#!/opt/py-env/bin python
# -*- encoding=utf-8 -*-
__author__ = "kailu"

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], ".."))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], "../../util"))

from itertools import product

import common.dicts as dicts
import db as dbcon
import loghelper as lghp

lghp.init_logger("gang", stream=True)
logger = lghp.get_logger("gang")


class GangTag(object):

    def __init__(self):
        global logger
        logger.info("init GangTag class.")
        self.gang_list = self._prepare_gangs()

        logger.info("prepare gang member names.")
        db = dbcon.connect_torndb()

        for gang in self.gang_list:
            relative_names = gang['relatives']

            query_s = ("SELECT id FROM company "
                       "WHERE name IN %s "
                       "AND (active is null OR active='Y')")
            r = db.query(query_s, relative_names)

            cids = [row['id'] for row in r]

            temp_members = []

            for cid in cids:
                names = self._get_all_member_names(cid)
                temp_members.extend(names)

            gang['members'] = set(temp_members)

    def _prepare_gangs(self):
        global logger
        logger.info("prepare gang dict and gang tag id.")

        db = dbcon.connect_torndb()

        query_s = ("SELECT id, name "
                   "FROM tag "
                   "WHERE type = 11053 "
                   "AND (active IS NULL OR active = 'Y');")
        r = db.query(query_s)

        gang_tag_name_id_dict = {row["name"]:row["id"]
                                 for row in r}

        gang_list = []
        for pair in dicts.get_gangs_relatives():
            gangname = pair[0]
            relative_name_list = pair[1:]
            if gangname in gang_tag_name_id_dict:
                gid = gang_tag_name_id_dict[gangname]
                gang_item = {"id": gid,
                             "name": gangname,
                             "relatives": relative_name_list}
                gang_list.append(gang_item)
            else:
                logger.warning("tag {} need to be checked.".format(gangname))

        db.close()

        return gang_list

    # get main member id list of a given cid
    def _get_main_member_list(self, cid):

        db = dbcon.connect_torndb()

        query_s = ("SELECT m.* FROM company_member_rel cmr, member m "
                   "WHERE cmr.memberId=m.id "
                   "AND cmr.companyId=%s "
                   "AND cmr.type in (5010, 5020) "
                   "AND (m.active is null OR m.active='Y') "
                   "AND (cmr.active is null OR cmr.active='Y');")
        r = db.query(query_s, cid)

        db.close()

        members = [{'id': row['id'],
                    'name': row['name'],
                    'education': row['education'] if row['education'] else u"",
                    'work': row['work'] if row['work'] else u""
                   } for row in r if row['name']]

        return filter(lambda x: x['name'] and 1 < len(x['name']) < 5, members)

    # get all member names of a given cid, mainly for gang companies
    def _get_all_member_names(self, cid):

        db = dbcon.connect_torndb()

        query_s = ("SELECT m.name FROM company_member_rel cmr, member m "
                   "WHERE cmr.memberId=m.id "
                   "AND cmr.companyId=%s "
                   # 有效 company member relation被清理过，故不做active限制
                   # 限制 member 的有效性
                   "AND (m.active is null OR m.active='Y');")
        r = db.query(query_s, cid)

        db.close()

        names = [row['name'] for row in r if row['name']]
        names = [name for name in names if len(name)>1 and len(name)<5]

        return names

    def predict(self, cid):

        result_tids = []

        members = self._get_main_member_list(cid)
        member_names = set([member["name"] for member in members])

        edus = filter(None, [member["education"] for member in members])
        works = filter(None, [member["work"] for member in members])
        member_backgrounds = edus + works

        # self._test_print(member_names)
        # self._test_print(member_backgrounds)

        for gang in self.gang_list:
            tid = gang["id"]
            gangname = gang["name"]
            gang_member_names = gang["members"]

            # self._test_print(gang_member_names)

            # 比较主要成员名字和潜在大公司的所有员工名字
            # 可能有重名 所以保证出现至少两次
            name_flags = member_names & gang_member_names
            if len(name_flags) > 1:

                # print "company {} has {} {} by common_members: ".format(cid, tid, gangname),
                # self._test_print(member_names & gang_member_names)

                result_tids.append(tid)
                continue

            relatives = set(gang["relatives"])
            # self._test_print(relatives)
            for relative, bg in product(relatives, member_backgrounds):
                if bg.find(relative) > -1:

                    # print "company {} has {} {} by member_backgrounds: ".format(cid, tid, gangname),
                    # self._test_print([bg])

                    result_tids.append(tid)
                    break

        return result_tids

    def _test_print(self, seq):
        for item in seq:
            print item,
        print


def test_dict():

    print "test get_gangs."

    gt = GangTag()
    dl = gt._prepare_gangs()
    for item in dl:
        print item


def test_all_member_list():

    print "test all member names"

    # Alibaba
    cid = 77301
    gt = GangTag()
    names = gt._get_all_member_names(cid)
    for name in names:
        print name


def test_init():

    print "test _init"

    gt = GangTag()
    for gang in gt.gang_list:
        print gang['name']
        for name in gang['members']:
            print name,
        print


def test_predict():

    print "test predict"

    # Baidu
    cid = 17105
    gt = GangTag()
    print gt.predict(cid)


def test_all():

    gt = GangTag()

    db = dbcon.connect_torndb()
    query_s = "select id, name, code from company where (active is null or active='Y');"
    r = [(row['id'], row['name'], row['code']) for row in db.query(query_s)]
    db.close()

    cids, cnames, ccodes = zip(*r)

    total = len(cids)

    ct = 0

    for i, cid in enumerate(cids):
        tids = gt.predict(cid)
        if i % 1000 == 0:
            print "-------- total:{} predicted:{} tagged:{} --------".format(total, i+1, ct)
        if tids:
            ct += 1
            print "{} {} has been tagged".format(cnames[i], ccodes[i])
            print "-------- total:{} predicted:{} tagged:{} --------".format(total, i+1, ct)

    print "total:{}, tagged:{}".format(total, ct)


def main():
    test_all()


if __name__ == "__main__":
    main()
