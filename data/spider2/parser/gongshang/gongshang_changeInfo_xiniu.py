# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import db, util, re
import pymongo

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

# logger
loghelper.init_logger("gongshang_changeInfo_xiniu", stream=True)
logger = loghelper.get_logger("gongshang_changeInfo_xiniu")

# mongo
mongo = db.connect_mongo()
collection_goshang = mongo.info.gongshang


def compare_gongshang(gongshangHistories, newGongshangchange):
    '''for A in As:
	for a in A:
		flag==false
		bnew=[]
		for b in B:
			if flag ==false:
				if a.date>b.date:bnew.append(a),flag=true
				if =:判断 item 是否一致，content 有没有内容
				if <:bnew.append(b)

		flag=false的 append 到 bnew 里

		B=bnew
'''
    # gongshangHistories=Histories[:1]
    # newGongshangchange= mongo.info.gongshang.find_one({'name': name})['changeInfo']
    for gongshangHistory in gongshangHistories:
        if gongshangHistory.has_key('changeInfo') is False: continue
        for changeA in gongshangHistory['changeInfo']:
            if changeA['changeItem'] in ['-', '', None] or changeA['changeTime'] in ['-', '', None]: continue
            logger.info('A: %s|%s', changeA['changeTime'], changeA['changeItem'])
            changeA['patched'] = True
            changeinfoNew = []
            flag = False
            for changeB in newGongshangchange:
                if flag is False:
                    if changeA['changeTime'] > changeB['changeTime']:
                        changeinfoNew.append(changeA)
                        flag = True
                    elif changeA['changeTime'] == changeB['changeTime']:
                        # print 'herer2'
                        if changeA['changeItem'] == changeB['changeItem']:
                            if changeB['contentBefore'] not in ['', '-', None] or changeB['contentAfter'] not in ['',
                                                                                                                  '-',
                                                                                                                  None]:
                                changeinfoNew.append(changeB)
                                # print 'here'
                                flag = True
                            else:
                                # print 'here1'
                                changeinfoNew.append(changeA)
                                flag = True
                    elif changeA['changeTime'] < changeB['changeTime']:
                        # print 'here3'
                        # logger.info('%s < %s',changeA['changeTime'],changeB['changeTime'])
                        pass

                if changeB not in changeinfoNew:
                    # print 'here4'
                    # logger.info('B: %s|%s', changeB['changeTime'], changeB['changeItem'])
                    changeinfoNew.append(changeB)
            if flag is False: changeinfoNew.append(changeA)
            newGongshangchange = changeinfoNew

    # newGongshangchange
    return newGongshangchange


def run():
    while True:
        gs = list(mongo.info.gongshang.find({"changeInfo_xiniu": {'$exists': False}}).limit(1000))
        for g in gs:
            Histories = list(mongo.info.gongshang_history.find({'name': g['name']}).sort("_id", pymongo.DESCENDING))
            newGongshangchange = g.get('changeInfo', [])
            newGongshangchange = compare_gongshang(Histories, newGongshangchange)
            logger.info('update %s', g['name'])
            mongo.info.gongshang.update_one({'_id': g['_id']},
                                            {'$set': {'changeInfo_xiniu': True, 'changeInfoXiniu': newGongshangchange,
                                                      'diffChecked': False}})
        if len(gs) == 0: break


if __name__ == "__main__":
    run()
