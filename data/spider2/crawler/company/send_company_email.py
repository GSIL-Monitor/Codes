# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
import xlwt

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper, extract, db, util, url_helper, download, traceback_decorator, email_helper

def send_jingdata_email():
    print('this time:%s to send email' % datetime.datetime.now())
    hour = time.localtime()[3]
    mongo = db.connect_mongo()
    collection = mongo.raw.jingdata_rz_incr
    if hour == 8:
        items = list(collection.find().sort('createtime', -1).limit(50))
    else:
        dd = datetime.date.today().strftime('%Y-%m-%d')
        items = list(collection.find({'Date': dd}))
    mongo.close()
    cnt = len(items)
    from_alias = 'Hush'
    reply_alias = 'Hush'
    reply_email = 'hush@xiniudata.com'
    # to = 'hush_guo@163.com'
    to = 'hush_guo@163.com;zhangli@xiniudata.com;wuwenxian@xiniudata.com;gewei@xiniudata.com;arthur@xiniudata.com;bamy@xiniudata.com'
    print('*******')
    subject = '鲸准日常融资事件'
    content = '<html>共<b>%d</b>起融资事件,请查看附件</html>' % cnt
    file = 'jingdata_rz_day.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('A Work Sheet')
    ws.write(0, 0, 'Product')
    ws.write(0, 1, 'Lunci')
    ws.write(0, 2, 'Date')
    ws.write(0, 3, 'Source')
    ws.write(0, 4, 'Jianjie')
    i = 1
    for item in items:
        product = item.get('name')
        lunci = item.get('phase')
        Date = item.get('Date')
        date = item.get('date')
        date = Date + ' ' + date
        jianjie = item.get('brief').decode('utf-8')
        source = item.get('link').decode('utf-8')
        if len(source) > 255:
            sources = source
        else:
            n = "HYPERLINK"
            sources = xlwt.Formula(n + '("%s";"%s")' % (source, source))
        ws.write(i, 0, product)
        ws.write(i, 1, lunci)
        ws.write(i, 2, date)
        ws.write(i, 3, sources)
        ws.write(i, 4, jianjie)
        i += 1
    wb.save(file)
    email_helper.send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file)
    print('done')

def send_qmp_email():
    print('this time:%s to send email' % datetime.datetime.now())
    hour = time.localtime()[3]
    mongo = db.connect_mongo()
    collection = mongo.raw.qmp_rz_incr
    if hour == 8:
        items = list(collection.find().sort('createtime', -1).limit(50))
    else:
        date = datetime.date.today().strftime('%Y-%m-%d')
        items = list(collection.find({'date': date}))
    mongo.close()
    cnt = len(items)
    from_alias = 'Hush'
    reply_alias = 'Hush'
    reply_email = 'hush@xiniudata.com'
    # to = 'hush_guo@163.com'
    to = 'hush_guo@163.com;zhangli@xiniudata.com;wuwenxian@xiniudata.com;gewei@xiniudata.com;arthur@xiniudata.com;bamy@xiniudata.com'
    print('*******')
    subject = '企名片日常融资事件'
    content = '<html>共<b>%d</b>起融资事件,请查看附件</html>' % cnt
    file = 'qmp_rz_day.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('A Work Sheet')
    ws.write(0, 0, 'Product')
    ws.write(0, 1, 'Lunci')
    ws.write(0, 2, 'Date')
    ws.write(0, 3, 'Source')
    ws.write(0, 4, 'Jianjie')
    i = 1
    for item in items:
        product = item.get('product')
        lunci = item.get('lunci')
        # Date = item.get('Date')
        date = item.get('news_time')
        # date = Date + ' ' + date
        jianjie = item.get('weiyu').decode('utf-8')
        source = item.get('qmp_url').decode('utf-8')
        if len(source) > 255:
            sources = source
        else:
            n = "HYPERLINK"
            sources = xlwt.Formula(n + '("%s";"%s")' % (source, source))
        ws.write(i, 0, product)
        ws.write(i, 1, lunci)
        ws.write(i, 2, date)
        ws.write(i, 3, sources)
        ws.write(i, 4, jianjie)
        i += 1
    wb.save(file)
    email_helper.send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file)
    print('done')

def send_tzj_email():
    print('this time:%s to send email' % datetime.datetime.now())
    hour = time.localtime()[3]
    mongo = db.connect_mongo()
    collection = mongo.raw.tzj_rz_incr
    if hour == 8:
        items = list(collection.find().sort('createtime', -1).limit(50))
    else:
        date = datetime.date.today().strftime('%Y-%m-%d')
        items = list(collection.find({'date': date}))
    mongo.close()
    cnt = len(items)
    from_alias = 'Hush'
    reply_alias = 'Hush'
    reply_email = 'hush@xiniudata.com'
    to = 'hush_guo@163.com;zhangli@xiniudata.com;wuwenxian@xiniudata.com;gewei@xiniudata.com;arthur@xiniudata.com;bamy@xiniudata.com'
    # to = 'hush_guo@163.com;zhangli@xiniudata.com;wuwenxian@xiniudata.com;gewei@xiniudata.com;arthur@xiniudata.com;bamy@xiniudata.com'
    print('*******')
    subject = '投资界日常融资事件'
    content = '<html>共<b>%d</b>起融资事件,请查看附件</html>' % cnt
    file = 'tzj_rz_day.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('A Work Sheet',cell_overwrite_ok=True)
    ws.write(0, 0, 'Product')
    ws.write(0, 1, 'Lunci')
    ws.write(0, 2, 'Date')
    ws.write(0, 3, 'Pro_Source')
    ws.write(0, 4, 'Invest_Source')
    ws.write(0, 5, 'Investment')
    i = 1
    for item in items:
        product = item.get('product')
        lunci = item.get('lunci')
        date = item.get('date')
        pro_source = item.get('project_url').decode('utf-8')
        invest_source = item.get('invest_url').decode('utf-8')
        investr = item.get('investr')

        if len(pro_source) > 255:
            sources1 = pro_source
        else:
            n = "HYPERLINK"
            sources1 = xlwt.Formula(n + '("%s";"%s")' % (pro_source, pro_source))
        if len(invest_source) > 255:
            sources2 = invest_source
        else:
            n = "HYPERLINK"
            sources2 = xlwt.Formula(n + '("%s";"%s")' % (invest_source, invest_source))
        ws.write(i, 0, product)
        ws.write(i, 1, lunci)
        ws.write(i, 2, date)
        ws.write(i, 3, sources1)
        ws.write(i, 4, sources2)
        ws.write(i, 5, investr)
        i += 1
    wb.save(file)
    email_helper.send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file)
    print('done')

def send_cyz_email():
    print('this time:%s to send email' % datetime.datetime.now())
    hour = time.localtime()[3]
    mongo = db.connect_mongo()
    collection = mongo.raw.cyz_rz_incr
    if hour == 8:
        items = list(collection.find().sort('createtime', -1).limit(50))
    else:
        date = datetime.date.today().strftime('%Y-%m-%d')
        items = list(collection.find({'date': date}))
    mongo.close()
    cnt = len(items)
    from_alias = 'Hush'
    reply_alias = 'Hush'
    reply_email = 'hush@xiniudata.com'
    to = 'hush_guo@163.com;zhangli@xiniudata.com;wuwenxian@xiniudata.com;gewei@xiniudata.com;arthur@xiniudata.com;bamy@xiniudata.com'
    # to = 'hush_guo@163.com;zhangli@xiniudata.com;wuwenxian@xiniudata.com;gewei@xiniudata.com;arthur@xiniudata.com;bamy@xiniudata.com'
    print('*******')
    subject = '创业邦日常融资事件'
    content = '<html>共<b>%d</b>起融资事件,请查看附件</html>' % cnt
    file = 'cyz_rz_day.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('A Work Sheet')
    ws.write(0, 0, 'Product')
    ws.write(0, 1, 'Lunci')
    ws.write(0, 2, 'Date')
    ws.write(0, 3, 'Pro_Source')
    ws.write(0, 4, 'Invest_Source')
    ws.write(0, 5, 'Investment')
    i = 1
    for item in items:
        product = item.get('product')
        lunci = item.get('lunci')
        date = item.get('date')
        pro_source = item.get('project_url').decode('utf-8')
        invest_source = item.get('invest_url').decode('utf-8')
        invests = item.get('investment')
        if len(pro_source) > 255:
            sources1 = pro_source
        else:
            n = "HYPERLINK"
            sources1 = xlwt.Formula(n + '("%s";"%s")' % (pro_source, pro_source))
        if len(invest_source) > 255:
            sources2 = invest_source
        else:
            n = "HYPERLINK"
            sources2 = xlwt.Formula(n + '("%s";"%s")' % (invest_source, invest_source))
        investr = ' '.join(invests)
        ws.write(i, 0, product)
        ws.write(i, 1, lunci)
        ws.write(i, 2, date)
        ws.write(i, 3, sources1)
        ws.write(i, 4, sources2)
        ws.write(i, 5, investr)
        i += 1
    wb.save(file)
    email_helper.send_mail_file(from_alias, reply_alias, reply_email, to, subject, content, file)
    print('done')

if __name__ == '__main__':
    send_jingdata_email()
    time.sleep(10)
    send_qmp_email()
    time.sleep(10)
    send_tzj_email()
    time.sleep(10)
    send_cyz_email()
