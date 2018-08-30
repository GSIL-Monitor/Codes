# coding=utf-8
__author__ = 'victor'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')

import time
from common.zhtools.segment import Segmenter


class PositionClassifier(object):

    def __init__(self):

        self.segmenter = Segmenter(cut_all=True)
        self.first_mapping = {
            1: u'技术',
            2: u'产品',
            3: u'设计',
            4: u'运营',
            5: u'市场',
            6: u'职能'
        }
        self.first_positions = dict.fromkeys(self.first_mapping.keys())
        self.train_first_positions()

    def train_first_positions(self):

        self.first_positions[1] = set([
            u'工程师', u'技术', u'java', u'python', u'php', u'c++', u'c', u'android', u'ios', u'测试',
            u'web', u'前端', u'数据库', u'ruby', u'perl', u'node.js', u'c#', u'go', u'html5', u'flash',
            u'javascript', u'u3d', u'运维', u'网络', u'安全', u'数据仓库', u'dba', u'mysql', u'oracle',
            u'sqlserver', u'sql', u'硬件', u'嵌入式', u'驱动', u'材料', u'开发'
        ])
        self.first_positions[2] = set([
            u'产品', u'产品经理', u'策划',
        ])
        self.first_positions[3] = set([
            u'设计', u'设计师', u'游戏', u'ui', u'ue',
        ])
        self.first_positions[4] = set([
            u'运营', u'coo', u'编辑', u'主编', u'文案', u'售前', u'售后', u'客服',
        ])
        self.first_positions[5] = set([
            u'市场', u'销售', u'seo', u'sem', u'商务', u'客户', u'bd', u'公关', u'采购', u'物流', u'仓储', u'广告', u'媒介',
            u'招商', u'推广'
        ])
        self.first_positions[6] = set([
            u'人事', u'hr', u'行政', u'培训', u'绩效', u'前台', u'总助', u'秘书', u'文秘', u'财务', u'会计', u'出纳',
            u'税务', u'审计', u'hrm', u'hrd', u'财务', u'法务', u'律师', u'专利', u'招聘'
        ])

    def get_first_positions(self):
        return self.first_positions.keys()

    def classify_first(self, position):

        position = set(map(lambda x: x.lower(), self.segmenter.cut(position)))
        return sorted([(k, len(position & v)) for k, v in self.first_positions.items()], key=lambda x: -x[1])[0][0]

    def get_first_name(self, key):

        return self.first_mapping.get(key)

if __name__ == '__main__':

    c = PositionClassifier()
    print c.classify_first(u'市场推广'), c.classify_first(u'java')
    print time.ctime()