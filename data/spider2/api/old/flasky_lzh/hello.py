from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from flask import make_response, send_file

import sys, os

sys.path.append(os.path.join(sys.path[0], '../work/tshbao/data/spider2/aggregator/funding'))
sys.path.append(os.path.join(sys.path[0], '../work/tshbao/data/util'))
sys.path.append(os.path.join(sys.path[0], '../work/tshbao/data/support'))
import funding_news_report

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

import pymongo

mongo = pymongo.MongoClient('localhost', 27017)

collection = mongo.article.news


class NameForm(Form):
    url = StringField('Enter the url?', validators=[Required()])
    submit = SubmitField('Submit')


class DateForm(Form):
    cid = StringField('Enter the companyId', validators=[])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/testdownload', methods=['GET'])
def testdownload():
    content = "long text"

    response = make_response(content)

    response.headers["Content-Disposition"] = "attachment; filename=myfilename.txt"

    return response


@app.route('/lzh', methods=['GET', 'POST'])
def lzh():
    import pandas as pd
    import numpy as np
    x = pd.DataFrame(np.random.randn(20, 5))
    return render_template("analysis.html", form=DateForm(), data=x, hasdata=1)
    # return render_template("analysis.html", form=DateForm())


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    import pandas as pd
    import numpy as np
    x = pd.DataFrame(np.random.randn(20, 5))
    form = DateForm()

    if form.validate_on_submit():
        cid = form.cid.data
        x = funding_news_report.run_test(cid)
        x.to_excel('test.xlsx')
        path = os.path.join(sys.path[0], 'test.xlsx')
        response = make_response(send_file(path))
        response.headers["Content-Disposition"] = "attachment; filename=companyId_%s.xlsx;" % cid
        return response
        # return render_template("analysis.html", form=form, data=x,hasdata=1)

    return render_template("analysis.html", form=form)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        url = form.url.data
        r = collection.find_one({'link': url})

        if r is None:
            newsid = 'url wrong or news not exists'
        else:
            newsid = 'http://xiniudata.com/#/news/%s'%str(r[u'_id'])

        session['newsid'] = newsid
        return redirect(url_for('index'))
    return render_template('index.html', form=form, newsid=session.get('newsid'))


if __name__ == '__main__':
    app.run()
