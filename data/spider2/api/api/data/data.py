# -*- coding: utf-8 -*-
from flask import request, make_response, json, g, current_app
import hashlib

from . import bp
# from flask_wtf import Form
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, PasswordField, RadioField, SelectMultipleField
from wtforms.validators import Required, DataRequired

from flask import make_response, send_file, render_template, session, redirect, url_for, flash
import os, sys
import pandas as pd

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../'))
import loghelper
import data_code
import datetime

# logger
loghelper.init_logger("crawler_evervc_company", stream=True)
logger = loghelper.get_logger("crawler_evervc_company")


# sys.path.append(os.path.join(sys.path[0], '../aggregator/funding'))
# sys.path.append(os.path.join(sys.path[0], '../../util'))
# sys.path.append(os.path.join(sys.path[0], '../../support'))
# import funding_news_report
#
# @bp.route('/get', methods=['GET'])
# def list():
#     sql = "select * from spider_stats order by id desc limit 100"
#
#     data = g.conn.query(sql)
#
#     result = {"code": 0,
#               "data": data,
#               }
#     return json.dumps(result)


class NameForm(Form):
    url = StringField('Enter the url?', validators=[], default='url')
    title = StringField('Enter the title?', validators=[], default='title')
    submit = SubmitField('Submit')


class StringForm(Form):
    string = StringField('Enter the string?', validators=[], default='string')
    submit = SubmitField('Submit')


class DateForm(Form):
    startDate = StringField('Enter the StartDate', validators=[Required()])
    endDate = StringField('Enter the EndDate,not required', validators=[], default=datetime.date.today())
    password = PasswordField('Password please', validators=[Required()])
    submit = SubmitField('Submit')


class DateForm2(Form):
    startDate = StringField('Enter the StartDate', validators=[Required()])
    endDate = StringField('Enter the EndDate,not required', validators=[], default=datetime.date.today())
    # Radio Box类型，单选框，choices里的内容会在ul标签里，里面每个项是(值，显示名)对
    location = RadioField('Country', choices=[('All', '全部'), ('CN', '国内'), ('EN', '国外')],
                          validators=[], default='All')
    round = SelectMultipleField('Round', choices=[
        ('0L', u'融资未知'),
        ('1000', u'\u672a\u878d\u8d44'),
        ('1009', u'\u4f17\u7b79'),
        ('1010', u'\u79cd\u5b50\u8f6e'),
        ('1011', u'\u5929\u4f7f\u8f6e'),
        ('1020', u'Pre-A\u8f6e'),
        ('1030', u'A\u8f6e'),
        ('1031', u'A+\u8f6e'),
        ('1039', u'Pre-B\u8f6e'),
        ('1040', u'B\u8f6e'),
        ('1041', u'B+\u8f6e'),
        ('1050', u'C\u8f6e'),
        ('1051', u'C+\u8f6e'),
        ('1060', u'D\u8f6e'),
        ('1070', u'E\u8f6e'),
        ('1080', u'F\u8f6e'),
        ('1090', u'\u540e\u671f\u9636\u6bb5'),
        ('1100', u'Pre-IPO'),
        ('1105', u'\u65b0\u4e09\u677f'),
        ('1106', u'\u65b0\u4e09\u677f\u5b9a\u589e'),
        ('1109', u'ICO'),
        ('1110', u'IPO'),
        ('1111', u'Post-IPO'),
        ('1112', u'\u4e3b\u677f\u5b9a\u589e'),
        ('1120', u'\u5e76\u8d2d'),
        ('1130', u'\u6218\u7565\u6295\u8d44'),
        ('1131', u'\u6218\u7565\u5408\u5e76'),
        ('1140', u'\u79c1\u6709\u5316'),
        ('1150', u'\u503a\u6743\u878d\u8d44'),
        ('1160', u'\u80a1\u6743\u8f6c\u8ba9'),
        ('1170', u'\u6276\u6301\u57fa\u91d1')
    ])

    tag = StringField('Enter the tags', validators=[], default='eg. 人工智能、电子商务')
    investor = StringField('Enter the investorId', validators=[], default='eg. 117、139')

    password = PasswordField('Password please', validators=[Required()])
    submit = SubmitField('Submit')


class DateForm_sfunding(Form):
    Date = StringField('Enter the Date', validators=[Required()])
    password = PasswordField('Password please', validators=[Required()])
    submit = SubmitField('Submit')


class DateForm_investorFundingCnt(Form):
    password = PasswordField('Password please', validators=[Required()])
    submit = SubmitField('Submit')


def run_tes(cid):
    sql = '''

    select * from company where id=%s limit 10

    '''

    results = g.conn2.query(sql, cid)
    df = pd.DataFrame(results)
    return df


@bp.route('/news_index', methods=['GET', 'POST'])
def news_index():
    import datetime, pymongo
    form = NameForm()
    collection = g.mongo.article.news_index
    r = list(collection.find({}, {'_id': 0}).sort("createTime", pymongo.DESCENDING).limit(20))
    import pandas as pd
    pd.set_option('max_colwidth', 2000)
    r = pd.DataFrame(r)
    if form.validate_on_submit():
        url = form.url.data

        collection.insert({'createTime': datetime.datetime.utcnow(), 'link': url, 'status': 'not available'})
        # session['newsid'] = newsid
        # return render_template('news_index.html', form=form, data=r, hasdata=1)
        return redirect('5977875df8716656636efb78' + url_for('.news_index'))
    return render_template('news_index.html', form=form, data=r, hasdata=1, string='news_index')


# @bp.route('/export2', methods=['GET', 'POST'])
# def analysis():
#     import pandas as pd
#     # import numpy as np
#     # x = pd.DataFrame(np.random.randn(20, 5))
#     form = DateForm()
#
#     if form.validate_on_submit():
#         startDate = form.startDate.data
#         endDate = form.endDate.data
#         password = form.password.data
#         if password != 'xiniu':
#             flash('wrong password!')
#             return render_template("analysis.html", form=form)
#
#         x, columns = data_code.run(g.conn, g.mongo, startDate, endDate)
#         x.to_excel('test.xlsx', index=0, columns=columns, encoding="utf-8")
#         path = os.path.join(sys.path[0], 'test.xlsx')
#         response = make_response(send_file(path))
#         response.headers["Content-Disposition"] = "attachment; filename=funding_news_report_%s~%s.xlsx;" % (
#             startDate, endDate)
#         return response
#         # return render_template("analysis.html", form=form, data=x,hasdata=1)
#
#     return render_template("analysis.html", form=form)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        url = form.url.data
        title = form.title.data
        collection = g.mongo.article.news
        logger.info('url:%s title:%s', url, title)
        r = collection.find_one({'$or': [{'link': url}, {'title': title.strip()}]})

        if r is None:
            newsid = 'url wrong or news not exists'
        else:
            newsid = 'http://pro.xiniudata.com/#/news/%s' % str(r[u'_id'])

        session['newsid'] = newsid
        logger.info(newsid)
        logger.info(url_for('api.data.index'))
        # logger.info( 'url here:%s',url_for('api.data.index',_external=True))
        # return redirect('5977875df8716656636efb78' + url_for('api.data.index'))
        return redirect(url_for('api.data.index'))
    return render_template('index.html', form=form, newsid=session.get('newsid'))


@bp.route('/sfunding', methods=['GET', 'POST'])
def sfunding():
    import pandas as pd
    form = DateForm_sfunding()

    if form.validate_on_submit():
        Date = form.Date.data
        password = form.password.data
        if password != 'xiniu':
            flash('wrong password!')
            return render_template("analysis.html", form=form)

        x = pd.DataFrame(data_code.extract_sf(g.conn, datetime.datetime.strptime(Date, "%Y-%m-%d").date()))

        x.to_excel('sfunding.xlsx', index=0, encoding="utf-8")
        path = os.path.join(sys.path[0], 'sfunding.xlsx')
        response = make_response(send_file(path))
        response.headers["Content-Disposition"] = "attachment; filename=sfunding_%s.xlsx;" % (Date)
        return response
        # return render_template("analysis.html", form=form, data=x,hasdata=1)

    return render_template("analysis.html", form=form)


@bp.route('/investorFundingCnt', methods=['GET', 'POST'])
def investorFundingCnt():
    import pandas as pd
    form = DateForm_investorFundingCnt()

    if form.validate_on_submit():
        password = form.password.data
        if password != 'xiniu':
            flash('wrong password!')
            return render_template("analysis.html", form=form)

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
        x = pd.DataFrame(list(g.mongo.investor.fundingcnt.find({'modifyTime': {'$gt': yesterday}})))
        # x = x.drop(['_id'], axis=1)
        x.to_excel('investorFundingCnt.xlsx', index=0, encoding="utf-8",
                   columns=["investorId", "investorName", u"是否上线", u"全名", u"短名", 'link', "2014", "2015", "2016",
                            "2017", '2018'])

        path = os.path.join(sys.path[0], 'investorFundingCnt.xlsx')
        response = make_response(send_file(path))
        response.headers["Content-Disposition"] = "attachment; filename=investorFundingCnt.xlsx;"
        return response
        # return render_template("analysis.html", form=form, data=x,hasdata=1)

    return render_template("analysis.html", form=form)


@bp.route('/newsSearch', methods=['GET', 'POST'])
def newsSearch():
    form = NameForm()
    if form.validate_on_submit():
        url = form.url.data
        title = form.title.data
        logger.info('newsSearch:%s', title)

        import requests
        import pandas as pd
        from bson import ObjectId
        pd.set_option('max_colwidth', 2000)

        data = u'{"input": "%s"}' % title

        j = requests.post('http://personal.xiniudata.com/api/search/universal_news', data=data.encode(),
                          headers={'Content-Type': 'application/json'}).json()
        # j=requests.post('http://personal.xiniudata.com/api/search/universal_news', data='{"input": "人工智能"}',
        #       headers={'Content-Type': 'application/json'}).json()

        if j.has_key('news'):
            # logger.info('here')
            newsids = [ObjectId(i) for i in j['news']['data']]

            collection = g.mongo.article.news
            r = list(collection.find({'_id': {'$in': newsids}}, {'title': 1, '_id': 1}))
            r = pd.DataFrame(r)
            return render_template('news_search.html', form=form, data=r, hasdata=1)
        else:
            logger.info('worng')
            logger.info(j)
            newsid = 'something wrong'

    return render_template('news_search.html', form=form, hasdata=0)


@bp.route('/blacklist', methods=['GET', 'POST'])
def blacklist():
    import datetime, pymongo
    form = StringForm()
    collection = g.mongo.blacklist.blacklist
    r = list(collection.find({}, {'_id': 0}).sort("createTime", pymongo.DESCENDING))
    import pandas as pd
    pd.set_option('max_colwidth', 2000)
    r = pd.DataFrame(r)
    if form.validate_on_submit():
        name = form.string.data
        name = name.strip()

        if name != 'string' and collection.find_one({'name': name}) is None:
            logger.info('inserting name to blacklist:%s', name)
            collection.insert(
                {'createTime': datetime.datetime.utcnow(), 'modifyTime': datetime.datetime.utcnow(), 'name': name,
                 'type': 3})
        # session['newsid'] = newsid
        # return render_template('news_index.html', form=form, data=r, hasdata=1)
        else:
            flash('already exists %s' % name)
        return redirect(url_for('.blacklist'))
    return render_template('news_index.html', form=form, data=r, hasdata=1, string='blacklist. 不要乱点哦！')


@bp.route('/funding', methods=['GET', 'POST'])
def funding2():
    import datetime, pymongo
    form = DateForm2()
    collection = g.mongo.task.data_report
    r = list(collection.find({}, {'_id': 0, 'param': 1, 'link': 1}).sort("createTime", pymongo.DESCENDING).limit(20))
    import pandas as pd
    pd.set_option('max_colwidth', 2000)
    r = pd.DataFrame(r)
    r['param'] = r.apply(lambda x: '; '.join(['%s:%s' % (c, x.param[c]) for c in x.param]), axis=1)
    logger.info('funding')

    if form.validate_on_submit():
        startDate = form.startDate.data
        endDate = form.endDate.data
        password = form.password.data
        location = form.location.data
        round = form.round.data
        tag = form.tag.data
        investor = form.investor.data

        if password != 'xiniu':
            flash('wrong password!')
            return render_template('news_index.html', form=form, data=r, hasdata=1, string='data_report')

        try:
            startDate2 = datetime.datetime.strptime(startDate, '%Y-%m-%d')
            endDate2 = datetime.datetime.strptime(endDate, '%Y-%m-%d')
        except:
            flash('wrong date pattern!')
            return redirect(url_for('.funding2'))

        if collection.find_one({'startDate': startDate, 'endDate': endDate}) is None:
            logger.info('inserting task :%s ~ %s', startDate, endDate)
            taskMap = {'createTime': datetime.datetime.utcnow()
                , 'modifyTime': datetime.datetime.utcnow()
                , 'param': {'startDate': str(startDate), 'endDate': str(endDate)}
                , 'processStatus': 0
                       }
            if location != 'All': taskMap['param']['location'] = location
            if round != []: taskMap['param']['round'] = round

            if tag not in ['eg. 人工智能、电子商务', '']: taskMap['param']['tag'] = tag
            if investor not in ['eg. 117、139', '']: taskMap['param']['investor'] = investor

            collection.insert(taskMap)

        # session['newsid'] = newsid
        # return render_template('news_index.html', form=form, data=r, hasdata=1)
        return redirect(url_for('.funding2'))
    return render_template('news_index.html', form=form, data=r, hasdata=1, string='data_report')


@bp.route('/charts', methods=['GET', 'POST'])
def charts():
    return render_template('charts.html')
