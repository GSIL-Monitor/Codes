# -*- coding: utf-8 -*-
__author__ = 'victor'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))

from common import dbutil
import db as dbcon

import numpy as np
from scipy.misc import imread
from wordcloud import WordCloud
from PIL import Image

# FONT_PATH = os.environ.get('FONT_PATH', 'simsun.ttf')
FONT_PATH = '/usr/share/fonts/SimSun.ttf'

tasks = [(1, u'戈壁创投', u'戈壁'),
         (2, u'梅花天使创投', u'梅花'),
         (3, u'原子创投', u'原子'),
         (4, u'熊猫资本', u'熊猫'),
         (5, u'明势资本', u'明势'),
         (6, u'丰厚资本', u'丰厚'),
         (9, u'华创资本', u'华创'),]

db = dbcon.connect_torndb()
# contents = dbutil.get_user_profile(db, 13, True).items()
for item in tasks:
    contents = dbutil.get_organization_profile(db, item[0], item[1])
    contents['o2o'] = contents.get('O2O')
    contents['O2O'] = 0
    for k, v in contents.iteritems():
        if not v:
            contents[k] = 0
    mask = np.array(Image.open(u'logs/%s.jpg' % item[2]))
    # mask = imread('tmp/avery_bw.png')
    wc = WordCloud(background_color='white', font_path=FONT_PATH, mask=mask)
    wc.generate_from_frequencies(contents.items())
    wc.to_file(u'tmp/%s_2014.6-now.png' % item[2])
db.close()