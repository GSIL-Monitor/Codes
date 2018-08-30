# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper
import db, datetime, email_helper, re
from urllib import unquote

# logger
loghelper.init_logger("search_stat", stream=True)
logger = loghelper.get_logger("search_stat")

DATE = None


def run_week():
    mongo = db.connect_mongo()
    conn = db.connect_torndb()

    # 获取上周日
    endDate = (datetime.datetime.today() - datetime.timedelta(days=time.localtime().tm_wday))
    endDate = datetime.datetime(endDate.year, endDate.month, endDate.day)
    # 获取上周一
    startDate = (datetime.datetime.today() - datetime.timedelta(days=time.localtime().tm_wday + 7))
    startDate = datetime.datetime(startDate.year, startDate.month, startDate.day)

    result = list(
        mongo.log.page_view.find(
            {'$and': [{'router': 'search'}, {'time': {'$gt': startDate - datetime.timedelta(hours=8)}}, {'time': {'$lt': endDate - datetime.timedelta(hours=8)}}]}, {'_id': 0}))
    import pandas as pd
    df = pd.DataFrame(result)
    df['time2']=df.apply(lambda x:x.time + datetime.timedelta(hours=8),axis=1)
    uids = [i['userId'] for i in result]

    result = conn.query('''select u.id userId,u.username userName,o.name orgName
    from user u 
    left join user_organization_rel r on r.userId=u.id
    left join organization o on r.organizationId=o.id
    where (r.active='Y' or r.active is null)
    and u.id in %s''', uids)

    df2 = pd.DataFrame(result)
    df3 = pd.merge(df, df2, on='userId', how='left')

    def keyword(x):
        if x.visitURL.find('open/') >= 0:
            keyword = x.visitURL.split('open/')[-1].strip()
        else:
            keyword = ''
        keyword = unquote(keyword.encode())
        return keyword.decode()

    df3['keyword'] = df3.apply(keyword, axis=1)

    df3['specialOrg'] = df3.apply(lambda x: ','.join(re.findall(u'烯牛|以太', x.orgName)) if pd.notnull(x.orgName) else '', axis=1)

    df3 = df3[df3.specialOrg != '烯牛']

    for c in df3.columns:
        def illegal(row):
            import re
            content = row[c]
            if content is not None:
                ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
                # print 'content:',c,content
                try:
                    content = ILLEGAL_CHARACTERS_RE.sub(r'', content)
                except:
                    pass
            return content

        # print 'c:',c
        df3[c] = df3.apply(illegal, axis=1)

    fileName = 'search_weekly_report.xlsx'
    df3.to_excel(fileName, index=0, columns=['visitURL', 'userName', 'orgName', 'ip', 'time2', 'keyword'])

    df3 = df3[df3.specialOrg == '']

    content = df3.orgName.value_counts().to_frame()[:10].to_html()
    content = '''<div>Dears,    <br /><br />

    附件是上周的用户搜索记录，搜索量前10的机构为：
    </div>
    ''' + content

    content2 = df3.keyword.value_counts().to_frame()[:100].to_html()
    content2 = '''
    <div>
    <br />
    前100名的搜索词为(统计已过滤掉以太和烯牛成员的搜索数据)：
    </div>
    
    ''' + content2

    content = content + content2

    # send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file)
    # 'zhlong@xiniudata.com;longzihao@foxmail.com',
    recieveList = ['avery', 'arthur','marchy', 'weiguangxiao', 'jiaojunpeng','charlotte','erin','jinglei','zhlong', 'bamy']
    # recieveList = ['zhlong','jiaojunpeng']

    path = os.path.join(sys.path[0], fileName)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "noreply@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in recieveList]),
                                "机构版（pro）上周搜索周报(%s ~ %s)" % (startDate.strftime('%Y-%m-%d'),
                                                     (endDate + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
                                                     ),
                                content, path)

    mongo.close()
    conn.close()


if __name__ == "__main__":
    global DATE
    while True:
        dt = datetime.datetime.now()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if datestr != DATE and dt.weekday() == 0:
            run_week()
            DATE = datestr
        time.sleep(60 * 60 * 23)
