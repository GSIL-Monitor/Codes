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
loghelper.init_logger("search_stat_personal", stream=True)
logger = loghelper.get_logger("search_stat_personal")

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
        mongo.log.user_log.find(
            {'$and': [{'url_type': 'front'}, {'requestURL': {'$regex': '/search'}},
                      {'time': {'$gt': startDate - datetime.timedelta(hours=8)}},
                      {'time': {'$lt': endDate - datetime.timedelta(hours=8)}}]}, {'_id': 0}))

    import pandas as pd
    df = pd.DataFrame(result)
    df['time2']=df.apply(lambda x:x.time + datetime.timedelta(hours=8),axis=1)

    uids = [i.get('userId') for i in result]

    result = conn.query('''select u.id userId,u.username userName,o.name orgName
    from user u 
    left join user_organization_rel r on r.userId=u.id
    left join organization o on r.organizationId=o.id
    where (r.active='Y' or r.active is null)
    and u.id in %s''', uids)

    df2 = pd.DataFrame(result)
    df3 = pd.merge(df, df2, on='userId', how='left')

    def keyword(x):
        if x.requestURL.find('search') >= 0:
            # keyword = x.requestURL.split('search/')[-1].split('&&name=')[-1].strip()
            keyword = x.requestURL.split('search/')[-1].split('&&name=')[-1].split('/search?name=')[-1].strip()
        else:
            keyword = ''
        keyword = unquote(keyword.encode())

        try:
            keyword = keyword.decode()
        except:
            keyword = ''
        return keyword

    df3['keyword'] = df3.apply(keyword, axis=1)
    # df3['keyword'] = df3.apply(lambda x: '(空搜索)' if pd.isnull(x.keyword) or x.keyword in ['/search', ''] else x.keyword,
    #                            axis=1)

    df3['specialOrg'] = df3.apply(lambda x: ','.join(re.findall(u'烯牛|以太', x.orgName)) if pd.notnull(x.orgName) else '',
                                  axis=1)

    # df3 = df3[df3.specialOrg != '烯牛']

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

    fileName = 'personal_search_weekly_report.xlsx'
    df3.to_excel(fileName, index=0, columns=['requestURL', 'userName', 'orgName', 'ip', 'time2', 'keyword'])

    hs=conn.query('''select * from hot_search limit 10''')
    hsString,updateTime='，'.join([i['name'] for i in hs]),hs[0]['modifyTime']
    # df3 = df3[df3.specialOrg == '']

    content2 = df3.keyword.value_counts().to_frame()[:100].to_html()
    content2 = '''
    <div>
    <div>Dears,    <br /><br />
    附件是上周个人版的用户搜索记录:
    <br /><br />
    1、上周个人版用户总计搜索了 <b>%s</b> 次
    <br /><br />
    2、这一周的热门搜索词是：<b>%s</b>；更新时间：%s
    <br /><br />
    3、前100名的搜索词为：
    </div>

    ''' % (df3.count()['code'],hsString,updateTime) + content2

    content = content2

    # send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file)
    # 'zhlong@xiniudata.com;longzihao@foxmail.com',
    # Avery, Arthur, Marchy, 广肖, 小娇, Charlotte, 刘林, 荆雷
    recieveList = ['avery', 'arthur', 'marchy', 'weiguangxiao', 'jiaojunpeng', 'charlotte', 'erin', 'jinglei', 'zhlong',
                   'bamy']
    # recieveList = ['zhlong']   #todo

    path = os.path.join(sys.path[0], fileName)
    email_helper.send_mail_file("烯牛数据数据开发组", "烯牛数据数据开发组", "zhlong@xiniudata.com",
                                ';'.join([i + '@xiniudata.com' for i in recieveList]),
                                "个人版上周搜索周报(%s ~ %s)" % (startDate.strftime('%Y-%m-%d'),
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
