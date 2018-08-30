# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import util

def getFundingRound(roundStr):
    fundingRound = 0
    if roundStr.startswith("尚未获投"):
        fundingRound = 1000
        roundStr = "尚未获投"
    elif roundStr.startswith("种子"):
        fundingRound = 1010
        roundStr = "天使轮"
    elif roundStr.startswith("天使"):
        fundingRound = 1010
        roundStr = "天使轮"
    elif roundStr.startswith("Pre-A"):
        fundingRound = 1020
        roundStr = "Pre-A轮"
    elif roundStr.startswith("A"):
        fundingRound = 1030
        roundStr = "A轮"
    elif roundStr.startswith("A+"):
        fundingRound = 1031
        roundStr = "A+轮"
    elif roundStr.startswith("Pre-B"):
        fundingRound = 1039
        roundStr = "Pre-B轮"
    elif roundStr.startswith("B"):
        fundingRound = 1040
        roundStr = "B轮"
    elif roundStr.startswith("B+"):
        fundingRound = 1041
        roundStr = "B+轮"
    elif roundStr.startswith("C"):
        fundingRound = 1050
        roundStr = "C轮"
    elif roundStr.startswith("D"):
        fundingRound = 1060
        roundStr = "D轮"
    elif roundStr.startswith("E"):
        fundingRound = 1070
        roundStr = "E轮"
    elif roundStr.startswith("F"):
        fundingRound = 1100
        roundStr = "F轮"
    elif roundStr.startswith("IPO") or roundStr.startswith("已上市") or roundStr.startswith("新三板"):
        fundingRound = 1110
        roundStr = "上市"
    elif roundStr.startswith("已被收购") or roundStr.startswith("并购"):
        fundingRound = 1120
        roundStr = "并购"
    elif roundStr.startswith("战略投资"):
        fundingRound = 1130
        roundStr = "战略投资"

    return fundingRound, roundStr

def getMoney(moneyStr):
    investment = 0
    currency = 3020
    precise = 'Y'

    investmentStr = ""

    if investment == 0:
        result = util.re_get_result(u'(数.*?)万元',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000
            elif investmentStr == u"数十":
                investment = 10*10000
            elif investmentStr == u"数百":
                investment = 100*10000
            elif investmentStr == u"数千":
                investment = 1000*10000
            elif investmentStr == u"数万":
                investment = 10000 * 10000
            elif investmentStr == u"数十万":
                investment = 100000 * 10000

    if investment == 0:
        result = util.re_get_result(u'(数.*?)亿元',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            precise = 'N'
        else:
            result = util.re_get_result(u'(数.*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                precise = 'N'

        if investmentStr != "":
            if investmentStr == u"数":
                investment = 1*10000*10000
            elif investmentStr == u"数十":
                investment = 10*10000*10000
            elif investmentStr == u"数百":
                investment = 100*10000*10000
            elif investmentStr == u"数千":
                investment = 1000*10000*10000
            elif investmentStr == u"数万":
                investment = 10000 * 10000 * 10000

    if investment == 0:
        result = util.re_get_result(u'(\d*?)万元',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(investmentStr) * 10000
        else:
            result = util.re_get_result(u'(\d*?)万美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(investmentStr) * 10000

    if investment == 0:
        result = util.re_get_result(u'(\d*\.?\d*?)亿元',moneyStr)
        if result != None:
            (investmentStr,) = result
            currency = 3020
            investment = int(float(investmentStr) * 100000000)
        else:
            result = util.re_get_result(u'(\d*\.?\d*?)亿美元',moneyStr)
            if result != None:
                (investmentStr,) = result
                currency = 3010
                investment = int(float(investmentStr) * 100000000)

    if investment == 0:
        result = util.re_get_result(u'亿元及以上美元',moneyStr)
        if result != None:
            currency = 3020
            investment = 100000000
            precise = 'N'
        else:
            result = util.re_get_result(u'亿元及以上',moneyStr)
            if result != None:
                currency = 3010
                investment = 100000000
                precise = 'N'

    return currency, investment, precise

def isRunnian(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False