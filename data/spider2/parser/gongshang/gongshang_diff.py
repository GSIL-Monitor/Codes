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
import gongshang_changeInfo_xiniu

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))

# logger
loghelper.init_logger("gongshang_diff", stream=True)
logger = loghelper.get_logger("gongshang_diff")

# mongo
mongo = db.connect_mongo()
collection_goshang = mongo.info.gongshang


def diff_capital(changeInfo):
    cnt = 0
    pattern = '\d+\.?\d*'
    for i in changeInfo:
        if i['changeItem'] is not None and i['changeItem'].find(u'注册资本') >= 0:
            logger.info('changeItem:%s|before:%s|after:%s', i['changeItem'], i['contentBefore'], i['contentAfter'])
            try:
                capitalBefore = float(re.findall(pattern, i['contentBefore'])[0])
            except:
                capitalBefore = 0
            try:
                capitalAfter = float(re.findall(pattern, i['contentAfter'])[0])
            except:
                capitalAfter = 0
            diffCapital = int(capitalAfter - capitalBefore)

            logger.info('cnt:%s|diffCapital:%s', cnt, diffCapital)
            logger.info('*' * 66)

            changeInfo[cnt]['diffCapital'] = diffCapital
        cnt += 1
    return changeInfo


def assign_id(changeInfo):
    ids = [int(i['id']) for i in changeInfo if i.has_key('id')]
    # current = max(ids) + 1 if len(ids) > 0 else 1
    current = 1

    cnt = -1

    for i in changeInfo[::-1]:
        # if i.has_key('id'):
        #     # logger.info('already has id:%s',i)
        #     pass
        # else:
        if 1:
            logger.info('no.%s changeInfo has no id, assign to %s', cnt, current)
            changeInfo[cnt]['id'] = current
            current += 1

        cnt -= 1
    return changeInfo


def diff(gongshang, key):
    cnt = 0

    for i in gongshang[key]:
        contentBefore = re.sub('</?em>|</?br>', '', i['contentBefore']) if i['contentBefore'] is not None else ''
        contentAfter = re.sub('</?em>|</?br>', '', i['contentAfter']) if i['contentAfter'] is not None else ''

        gongshang[key][cnt]['contentBefore'] = contentBefore
        gongshang[key][cnt]['contentAfter'] = contentAfter

        if i['changeItem'] is not None and (i['changeItem'].find(u'投资人') >= 0 or i['changeItem'].find(u'股东变更')) >= 0:
            logger.info('before:%s|after:%s', contentBefore, contentAfter)
            # pattern = u'\%|\.|企业法人|自然人股东|企业股东|法人股东|-|合伙企业|姓名:|股东:|股东名称：|企业名称:|投资人：|出资方式|货币|出资|证照号码|百分比:'
            # before = re.sub(pattern, '', contentBefore)
            before = re.sub(u'\d+|,|，', ';', contentBefore)
            before = re.sub(u'；', ';', before)
            # after = re.sub(pattern, '', contentAfter)
            after = re.sub(u'\d+|,|，', ';', contentAfter)
            after = re.sub(u'；', ';', after)

            def strip_list(list):
                cnt = 0
                for i in list:
                    list[cnt] = i.strip()
                    cnt += 1
                return list

            x = set(strip_list(before.split(';')))
            y = set(strip_list(after.split(';')))

            # USELESS=['%','.',u'企业法人',u'自然人股东',u'企业股东',u'法人股东']
            diff = [d.strip() for d in x ^ y]
            diffBefore, diffAfter = [], []

            for d in diff:
                # 沈洁（
                pattern = u'\（$|\($|:$|：$'
                d = re.sub(pattern, '', d)

                # other than words and ()
                pattern = u'[^\u4E00-\u9FA5A-Za-z0-9\(\)（）:： ]'
                d = re.sub(pattern, '', d)

                pattern = u'\%|\.|企业法人|自然人股东|企业股东|法人股东|-|合伙企业|姓名:|股东:|股东名称：|企业名称:|投资人：|出资方式|货币|出资|证照号码|百分比:|名称：'
                d_pre = re.sub(pattern, '', d).strip()
                if len(d_pre) == 0:
                    logger.info('trash info: %s', d)
                    continue

                logger.info('d:%s', d)
                patternFinal = u'\%|\.|企业法人|自然人股东|企业股东|法人股东|-|姓名:|股东:|股东名称：|企业名称:|投资人：|出资方式|货币|出资|证照号码|百分比:|名称：'

                if d in before and d not in after:
                    d = re.sub(patternFinal, '', d).strip()
                    diffBefore.append(d)
                elif d not in before and d in after:
                    foundFlag = False
                    if gongshang.has_key('investors'):
                        for investor in gongshang['investors']:
                            # logger.info('d:%s | in:%s', d, investor['name'])
                            if investor['name'] is None: continue
                            if d.find(investor['name']) >= 0:
                                logger.info('correct name from %s to %s', d, investor['name'])
                                diffAfter.append(investor['name'])
                                foundFlag = True
                                break

                    if foundFlag == False:
                        d = re.sub(patternFinal, '', d).strip()
                        diffAfter.append(d)
                # before:杭州嬴湖创造投资（有限合伙） after:股东: 杭州嬴湖创造投资（有限合伙）
                elif d in before and d in after:
                    pass
                else:
                    logger.info('%s wrong!!|%s', d, gongshang['name'])
                    logger.info('before:%s|after:%s', x, y)
                    # exit()

            logger.info(gongshang['name'])
            logger.info('*' * 66)

            gongshang[key][cnt]['diffBefore'] = diffBefore
            gongshang[key][cnt]['diffAfter'] = diffAfter

        cnt += 1
    return gongshang[key]


def run_tes():
    mongo = db.connect_mongo()
    collection_goshang = mongo.info.gongshang
    result = list(collection_goshang.find({'name': {'$in': ['深圳华大基因股份有限公司', '北京六合华大基因科技有限公司']}}))
    # result = list(collection_goshang.find({'name': {'$in': ['北京市爱迪通信有限责任公司', '哎哎信息科技（上海）有限公司']}}))
    for i in result:
        logger.info('processing %s', i['name'])
        newChangeInfo = diff(i, 'changeInfo')
        newChangeInfo = assign_id(newChangeInfo)
        id = i['_id']
        collection_goshang.update({'_id': id}, {'$set': {'changeInfo': newChangeInfo}})


def unset(gongshang):
    cnt = 0
    for i in gongshang['changeInfo']:
        if i['changeItem'].find(u'投资人') >= 0:
            gongshang['changeInfo'][cnt].pop('diff')
        cnt += 1

    return gongshang['changeInfo']


def tes_gudong(gongshang):
    cnt = 0
    for i in gongshang['changeInfo']:
        # if i['changeItem'].find(u'股东变更') >= 0:
        if i['changeItem'].find(u'注册资本') >= 0:
            print i['changeItem'], i['contentBefore'], i['contentAfter']
        cnt += 1


def run(flag):
    mongo = db.connect_mongo()
    collection_goshang = mongo.info.gongshang
    start = 0
    while True:
        if flag == 'incr':
            results = list(collection_goshang.find({"diffChecked": {"$ne": True}}).limit(1000))
        elif flag == 'all':
            results = list(collection_goshang.find({}).skip(start).limit(1000))
            start += 1000
        else:
            results = list(collection_goshang.find({"name": flag}))

        for i in results:
            id = i['_id']
            logger.info('processing %s', i['name'])

            if i.has_key('changeInfo'):
                # newChangeInfo = unset(i)
                # tes_gudong(i)
                # continue

                # newGongshang = changeinfo_patch(i)
                newChangeInfo = diff(i, 'changeInfo')
                newChangeInfo = assign_id(newChangeInfo)
                newChangeInfo = diff_capital(newChangeInfo)
                collection_goshang.update({'_id': id}, {'$set': {'changeInfo': newChangeInfo}})
                # collection_goshang.update({'_id': id}, {'$set': {'changeInfoXiniu': newChangeInfo}})

            if i.has_key('changeInfoXiniu') is False and i.has_key('changeInfo'):i['changeInfoXiniu'] = i['changeInfo']

            if i.has_key('changeInfoXiniu'):
                # newChangeInfo = unset(i)
                # tes_gudong(i)
                # continue
                if i.has_key('changeInfo'):
                    i['changeInfoXiniu'] = gongshang_changeInfo_xiniu.compare_gongshang([{'changeInfo': i['changeInfoXiniu']}],
                                                                            i['changeInfo'])

                    newChangeInfo = diff(i, 'changeInfoXiniu')
                    newChangeInfo = assign_id(newChangeInfo)
                    newChangeInfo = diff_capital(newChangeInfo)
                    collection_goshang.update({'_id': id}, {'$set': {'changeInfoXiniu': newChangeInfo,'changeInfo_xiniu': True}})
                else:
                    collection_goshang.update({'_id': id}, {'$set': {'changeInfo_xiniu': True}})


            collection_goshang.update({'_id': id}, {'$set': {'diffChecked': True}})

        if len(results) == 0 or (flag != 'all' and flag != 'incr'): break


def changeinfo_patch(gongshang):
    cnt = 0

    newchangeinfo = []
    for i in gongshang['changeInfo']:
        if i['changeItem'] is not None and (i['changeItem'].find(u'投资人') >= 0 or i['changeItem'].find(u'股东变更')) >= 0:
            if i['contentBefore'] == '-' and i['contentAfter'] == '-':
                # corporate active
                for his in list(
                        mongo.info.gongshang_history.find({'source': 13093, 'name': gongshang['name']}).sort("_id",
                                                                                                             pymongo.DESCENDING)):
                    changehis = his['changeInfo']
                    # 遍历某一条 history 的 changeinfo
                    for changehisitem in changehis:
                        if changehisitem['changeTime'] == i['changeTime'] and changehisitem['changeItem'] == i[
                            'changeItem']:
                            contentBeforeOld = changehisitem['contentBefore']
                            contentAfterOld = changehisitem['contentAfter']
                            break
                    if contentBeforeOld != '-' or contentAfterOld != '-':
                        # gongshang['changeInfo'][cnt + 1]['contentBefore'] = contentBeforeOld
                        # gongshang['changeInfo'][cnt + 1]['contentAfter'] = contentAfterOld
                        # gongshang['changeInfo'][cnt + 1]['patched'] = True
                        infoitem = {'contentBefore': contentBeforeOld,
                                    'contentAfter': contentAfterOld,
                                    'changeItem': i['changeItem'],
                                    'changeTime': i['changeTime'],
                                    'patched': True
                                    }
                        newchangeinfo.append(infoitem)
                        cnt += 1
                        break

            logger.info('*' * 66)
        newchangeinfo.append(i)

        cnt += 1
    gongshang['changeInfo'] = newchangeinfo
    return gongshang


# def full_patch():
#     name = u'中腾信金融信息服务（上海）有限公司'
#     name = u'西安知象光电科技有限公司'
#     Histories = list(mongo.info.gongshang_history.find({'name': name}).sort("_id", pymongo.DESCENDING))
#     newGongshangchange= mongo.info.gongshang.find_one({'name': name}).get('changeInfo',[])
#     result=compare_gongshang(Histories, newGongshangchange)
#     len(result)



if __name__ == "__main__":
    # run('all')
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        run(flag)
    else:
        while True:
            run('incr')
            logger.info('all done,sleep')
            time.sleep(60 * 1)
