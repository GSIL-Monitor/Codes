# coding=utf-8
__author__ = 'victor'

import os
import sys
reload(sys)
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.setdefaultencoding('utf-8')

import db as dbcon
from common import dbutil
from email_helper import send_mail

import codecs
from datetime import datetime, timedelta


def update_share_holders():

    db = dbcon.connect_torndb()
    mongo = dbcon.connect_mongo()
    investors = set(dbutil.get_online_investors(db)) & set(dbutil.get_famous_investors(db))
    investors = {iid: [i[1] for i in dbutil.get_investor_gongshang_with_ids(db, iid)] for iid in investors}
    with codecs.open('cach/famous.new', 'w', 'utf-8') as fo:
        for iid, imajias in investors.iteritems():
            iname = dbutil.get_investor_name(db, iid)
            for majia in imajias:
                try:
                    gs = mongo.info.gongshang.find_one({'name': majia})
                    if not gs:
                        continue
                    share_holers = gs.get('investors', [])
                    share_holers = [i.get('name') for i in share_holers if i.get('name') not in imajias]
                    share_holers = [i for i in share_holers if len(i) > 5]
                    if not share_holers:
                        fo.write('%s\t%s\n' % (iname, majia))
                    else:
                        for sh in share_holers:
                            fo.write('%s\t%s\t%s\n' % (iname, majia, sh))
                except Exception, e:
                    print majia, e
    caches = [line.strip() for line in codecs.open('cach/famous.cach', encoding='utf-8')]
    news = [line.strip() for line in codecs.open('cach/famous.new', encoding='utf-8')
            if u'西藏源融投资管理合伙企业' not in line]
    this_week = '%s ~ %s' % ((datetime.now()-timedelta(days=7)).strftime('%m月%d日'), datetime.now().strftime('%m月%d日'))
    if news:
        updates = [line for line in news if line not in caches]
        contents = u'Hi Victor,<br><br>' \
                   u'本周为您追踪到如下机构股东动态。<br>' \
                   u'追踪时间：%s<br><br>' \
                   u'%s <br><br>' \
                   u'以上为本次追踪内容。<br>如有疑问，欢迎联系我们：）<br>' \
                   u'烯牛数据团队<br>www.xiniudata.com' % (this_week, '<br>'.join(updates))
        title = u'机构股东动态 %s' % this_week
        send_mail(u'烯牛数据', u'烯牛数据', u'noreply@xiniudata.com', u'victor@xiniudata.com', title, contents)


if __name__ == '__main__':

    update_share_holders()
