# -*- coding: utf-8 -*-
import os, sys, datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import db


def insert_contest_user(contest_id, topic_id, stage_id, org_id, user_id):
    conn = db.connect_torndb()
    co = conn.get("select * from contest_organization where organizationId=%s and contestId=%s",
                  org_id, contest_id)
    if co is None:
        contestOrganizationId = conn.insert("insert contest_organization(organizationId,contestId,role,createTime,createUser,joinStatus) "
                "values(%s,%s,0,now(),1,57010)",
                                            org_id, contest_id)
        conn.insert("insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser) "
                "values(%s,%s,now(),1)",
                    contestOrganizationId, topic_id)
    u = conn.get("select * from stage_user_rel where stageId=%s and userId=%s",
                 stage_id, user_id)
    if u is None:
        conn.insert("insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser) "
                "values(%s,%s,'Y','N',now(),1)",
                    user_id, stage_id)
    conn.close()
    print "Ok."

def usage():
    print "python insert_contest_user.py contestId topicId stageId organizationId userId"


if __name__ == "__main__":
    if len(sys.argv) != 6:
        usage()
        exit()
    ts = sys.argv
    insert_contest_user(ts[1],ts[2],ts[3],ts[4],ts[5])