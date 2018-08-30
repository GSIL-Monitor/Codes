# coding=utf-8
__author__ = 'victor'

import sys
sys.path.append('..')
sys.path.append('../..')
reload(sys)

import codecs
import torndb
from common.zhtools.segment import Segmenter
from common.classifier.field import FieldClassifier

if __name__ == '__main__':

    sql = 'select dealId,dealname,dealdesc from deal where joinDemoDay=2;'
    db = torndb.Connection('localhost:3306', 'demoday', 'root', '')
    clf = FieldClassifier(model='lr')
    seg = Segmenter()
    # clf.train()

    fo = codecs.open('tmp', 'w', 'utf-8')
    for rid, result in enumerate(db.query(sql)):
        did, doc = result.dealId, result.dealdesc
        try:
            label = clf.naive_classify(seg.cut(doc))
            if label:
                print did, label
                fo.write('%s#%s\n' % (did, label[0]))
        except Exception, e:
            print did, 'fail'
            print e
        # if rid > 40:
        #     break

    fo.close()
    db.close()