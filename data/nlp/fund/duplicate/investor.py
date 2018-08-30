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

import StringIO
import gridfs
from wordcloud import WordCloud

FONT_PATH = '/usr/share/fonts/SimSun.ttf'


class InvestorProfile(object):

    def __init__(self):

        self.db = dbcon.connect_torndb()
        self.mongo = dbcon.connect_mongo()
        self.gfs = gridfs.GridFS(self.mongo.gridfs)

    def plot(self, iid):

        global FONT_PATH
        contents = dbutil.get_investor_profile(self.db, iid)
        contents['o2o'] = contents.get('O2O')
        contents['O2O'] = 0
        for k, v in contents.iteritems():
            if not v:
                contents[k] = 0
        wc = WordCloud(background_color='white', font_path=FONT_PATH)
        wc.generate_from_frequencies(contents)
        # wc.to_file('dumps/tmp.png')
        tmp = wc.to_image()
        data = StringIO.StringIO()
        tmp.save(data, 'png')
        mid = self.gfs.put(data.getvalue(), content_type='png', filename='%s.all.png' % str(iid))
        print mid

if __name__ == '__main__':

    ir = InvestorProfile()
    ir.plot(122)