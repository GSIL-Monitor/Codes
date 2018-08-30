# -*- coding: utf-8 -*-
import os, sys
import datetime
import xlwt

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config, util, db

#logger
loghelper.init_logger("audi_export", stream=True)
logger = loghelper.get_logger("audi_export")

mongo = db.connect_mongo()
collection = mongo.demoday.contest_company

def get_topic(topic_id):
    if topic_id == 13:
        return u"人工智能的应用"
    if topic_id == 11:
        return u"数字化"
    if topic_id == 12:
        return u"车·生活"
    return ""

def get_contest_company_stage_status(status):
    if status == 56020:
        return u"通过"
    if status == 56030:
        return u"未通过"
    return ""

columns = [
    u"项目概念／愿景",
    u"项目介绍",
    u"姓名",
    u"公司名",
    u"联系电话",
    u"其他联系电话",
    u"电子邮箱地址",
    u"微信号"
]

def process(contest_id, stage_id):
    style_date = xlwt.easyxf(num_format_str='yyyy/MM/dd hh:mm:ss')

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Audi')

    #
    line = 0
    col = 0
    ws.write(line,col,""); col+=1
    ws.write(line,col,"ID"); col+=1
    ws.write(line,col,u"创建时间"); col+=1
    ws.write(line,col,u"项目名"); col+=1
    ws.write(line,col,u"主题"); col+=1
    for column in columns:
        ws.write(line,col,column); col+=1
    ws.write(line,col,u"是否通过"); col+=1
    ws.write(line,col,u"平均分"); col+=1
    ws.write(line,col,u"打分人"); col+=1

    conn =db.connect_torndb()
    stage_score_dimensions = conn.query("select * from stage_score_dimension "
                                        "where stageId=%s order by sort",
                                        stage_id)
    for d in stage_score_dimensions:
        ws.write(line,col,d["name"]); col+=1
    ws.write(line,col,u"评论人"); col+=1
    ws.write(line,col,u"评论时间"); col+=1
    ws.write(line,col,u"评论"); col+=1

    contest_company_stages = conn.query("select * from contest_company_stage "
                                        "where stageId=%s order by id",
                                        stage_id)

    num = 1
    for contest_company_stage in contest_company_stages:
        contest_company_id = contest_company_stage["contestCompanyId"]
        if contest_company_stage["score"] is None:
            continue

        line += 1; col = 0
        ws.write(line,col,num); col+=1; num += 1

        contest_company = conn.get("select * from contest_company where id=%s", contest_company_id)
        print contest_company["name"], get_topic(contest_company["topicId"])
        ws.write(line,col,contest_company["id"]); col+=1
        ws.write(line,col,contest_company["createTime"], style_date); col+=1
        ws.write(line,col,contest_company["name"]); col+=1
        ws.write(line,col,get_topic(contest_company["topicId"])); col+=1

        contest_company_mongo = collection.find_one({"contestCompanyId":contest_company_id})
        for column in columns:
            found = False
            for item in contest_company_mongo["extra"]:
                if column == item["name"]:
                    print column, item["value"]
                    ws.write(line,col,item["value"]); col+=1
                    found = True
            if found is False:
                ws.write(line,col,""); col+=1
        ws.write(line,col,get_contest_company_stage_status(contest_company_stage["status"])); col+=1
        ws.write(line,col,contest_company_stage["score"]); col+=1

        line_score = line
        score_users = conn.query("select distinct userId from contest_company_score "
                                 "where contestCompanyId=%s order by userId",
                                 contest_company_id)
        for score_user in score_users:
            col_score = col
            user = conn.get("select * from user where id=%s", score_user["userId"])
            print user["username"]
            ws.write(line_score, col_score,user["username"]); col_score+=1

            for dimension in stage_score_dimensions:
                score = conn.get("select * from contest_company_score "
                                 "where contestCompanyId=%s and userId=%s and stageScoreDimensionId=%s",
                                 contest_company_id, score_user["userId"], dimension["id"])
                print dimension["name"]
                if score is not None:
                    print score["score"]
                    ws.write(line_score, col_score,score["score"]); col_score+=1
                else:
                    ws.write(line_score, col_score,""); col_score+=1
            line_score += 1

        line_comment = line
        comments = conn.query("select * from stage_contest_company_user_comment "
                              "where contestCompanyId=%s",
                              contest_company_id)
        for comment in comments:
            col_comment = col + len(stage_score_dimensions)+1
            comment_user = conn.get("select * from user where id=%s", comment["userId"])
            print comment_user["username"], comment["comment"]
            ws.write(line_comment, col_comment,comment_user["username"]); col_comment+=1
            ws.write(line_comment, col_comment,comment["createTime"], style_date); col_comment+=1
            ws.write(line_comment, col_comment,comment["comment"]); col_comment+=1
            line_comment += 1

        if line_score > line or line_comment > line:
            if line_score > line_comment:
                line = line_score
            else:
                line = line_comment
            line -=1

        print "average: ", contest_company_stage["score"], get_contest_company_stage_status(contest_company_stage["status"])

        #test
        #if line>10:
        #    break
    conn.close()

    wb.save("logs/audi_export.xls")


if __name__ == "__main__":
    contest_id = 10
    stage_id = 11
    process(contest_id, stage_id)