# -*- coding:utf-8 -*-

import fasttext
import os
import sys
import itertools
import re
import json
import codecs
import pandas as pd
import numpy as np
from pandas import DataFrame
reload(sys)
sys.setdefaultencoding('utf-8')
ensure_ascii=False

list_key = [u'705', u'556', u'65', u'81', u'1713', u'22', u'290548', u'47', u'42', u'107', u'328', u'1672', u'599873',
            u'69360', u'636', u'758', u'309067', u'307', u'557285', u'2127', u'115482', u'431', u'604330',u'175747']
list_value = [u'705', u'556', u'65', u'81', u'1713', u'22', u'290548', u'47', u'42', u'107', u'328', u'1672', u'599873',
              u'69360', u'636', u'758', u'309067', u'307', u'557285', u'2127', u'115482', u'431', u'604330', u'175747']


def model(**kwargs):
    dict_number = {}
    # 训练模型
    trainpath = os.getcwd()[:14] + '/modeltotal3/train3wadd1.txt'
    textpath = os.getcwd()[:14] + '/train/testdata.txt'
    modelpath = os.getcwd()[:14] + '/modeltotal3/train1'
    modelpath_1 = os.getcwd()[:14] + '/modeltotal3/train1100_0.1_10_ns.bin'
    # modelpath_23 = os.getcwd()[:14] + '/model/20171221.bin'
    # load训练好的模型
    classifier_1 = fasttext.load_model(modelpath_1, label_prefix='__label__')
    # # classifier_23 = fasttext.load_model(modelpath_23, label_prefix='__label__')
    #预测
    with codecs.open(textpath, "rb",'utf-8') as dtrain:
        content = dtrain.read()
        content_split= content.split('\n')
        # count = 0
        # list_predict = []
        # list_really = []
        for m in list_key:
            for n in list_value:
                dict_number[(m,n)] = 0
        for i in range(0,len(content_split)-1):
            datalabel = content_split[i].split('__label__')
            data = datalabel[0]
            label = datalabel[1]
            dict = {}
            list = []
            list.append(data)
            # list_really.append(match)
            result = classifier_1.predict(list)
            dict_number[(result[0][0],label)]+=1
            dict[result[0][0]] = list[0]

            # with codecs.open('/Users/zlz/zlz/modeltotal2/predict7.txt', "a+", 'utf-8') as dtrain:
            #     json_str = json.dumps(dict, ensure_ascii=False)
            #     dtrain.write(json_str + '\n')

    return dict_number
#生成excel表格
def Statistics(dict_number):
    df1 = pd.DataFrame(index=list_key,columns=list_value)
    for i in list_key:
        for j in list_value:
            df1[j][i] = dict_number[(i,j)]
    writer = pd.ExcelWriter('/Users/zlz/zlz/modeltotal3/train3wadd1.xlsx')
    df1.to_excel(writer,'sheet1')
    writer.save()
    #调参
    # # 学习率lr，隐层的维数dim，n - grams的长度-ws等。
    # params = {'dim': [100, 150], 'lr': [0.1, 0.5, 1], 'loss': ['ns', 'hs'], 'ws': [5, 10]}
    # for k, v in kwargs.items():
    #     params[k] = v
    # keys, values = params.keys(), params.values()
    # best, best_score = '', 0
    # for p in itertools.product(*values):
    #     ps = {keys[i]: p[i] for i in xrange(4)}
    #     clf = fasttext.supervised(trainpath, modelpath + '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3]), label_prefix='__label__',**ps)
    #     result = clf.test(textpath)
    #     print '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3])
    #     print 'Precision: %.2f%%' % (result.precision * 100)
    #     print 'Recall Rate: %.2f%%\n' % (result.recall * 100)
    #
    #     f1 = float(2.0 * result.precision * result.recall) / float(result.precision + result.recall)
    #     if best_score < f1:
    #         best, best_score,  = '%s_%s_%s_%s' % (p[0], p[1], p[2], p[3]), f1
    # print '%s\n%.2f' % (best, best_score)

if __name__ == "__main__":
    # model()
    dict_number = model()
    Statistics(dict_number)

