#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-

ROUND = {
    1009: "众筹",
    1010: "种子轮",
    1011: "天使轮",
    1020: "Pre-A轮",
    1030: "A轮",
    1031: "A+轮",
    1039: "Pre-B轮",
    1040: "B轮",
    1041: "B+轮",
    1050: "C轮",
    1051: "C+轮",
    1060: "D轮",
    1070: "E轮",
    1080: "F轮",
    1090: "后期阶段",
    1100: "Pre-IPO",
    1105: "新三板",
    1106: "新三板定增",
    1109: "ICO",
    1110: "IPO",
    1111: "Post-IPO",
    1112: "定向增发",
    1120: "并购",
    1130: "战略投资",
    1131: "战略合并",
    1140: "私有化",
    1150: "债权融资",
    1160: "股权转让"
}

CURRENCY = {
    3010: "美元",
    3020: "人民币",
    3030: "新加坡元",
    3040: "欧元",
    3050: "英镑",
    3060: "日元",
    3070: "港币",
    3080: "澳元"
}


def get_round_desc(round):
    return ROUND.get(round, "轮次未知")


def gen_investment_desc(num, precise, preciseDesc, currency):
    if preciseDesc is not None and preciseDesc.strip() != "":
        return preciseDesc.strip()

    if num is None or num < 10000:
        return "金额未知"

    _str = ""
    if precise == 'N':
        _temp = str(int(num))
        l = len(_temp)
        if l <= 5:
            _str = "数万"
        elif l == 6:
            _str = "数十万"
        elif l == 7:
            _str = "数百万"
        elif l == 8:
            _str = "数千万"
        elif l == 9:
            _str = "数亿"
        elif l == 10:
            _str = "数十亿"
        else:
            _str = "百亿以上"
    else:
        if num > 10000 and num < 10000 * 10000:
            _num1 = int(num/10000)
            _num2 = int(num%10000/100)
            _str = "%s" % _num1
            if _num2 > 0:
                _str = "%s.%s" % (_str, _num2)
            _str = "%s万" % _str
        else:
            _num1 = int(num / 10000 / 10000)
            _num2 = int(num % 100000000 / 10000 / 100)
            _str = "%s" % _num1
            if _num2 > 0:
                _str = "%s.%s" % (_str, _num2)
            _str = "%s亿" % _str

    _currency = CURRENCY.get(currency, "")
    return "%s%s" % (_str, _currency)


def gen_investors(investorsRaw, investors):
    if investors is None and investorsRaw is None:
        return "未透露"
    if investors is None:
        return investorsRaw

    # _str=""
    # items = json.loads(investors)
    # conn = db.connect_torndb()
    # for item in items:
    #     if item["type"] == "investor":
    #         investor_id = item["id"]
    #         investor = conn.get("select * from investor where id=%s", investor_id)
    #         if investor is not None and investor["active"] !='N' and investor["online"]=='Y':
    #             _str += '<a href="http://www.xiniudata.com/#/investor/%s/overview">%s</a>' % (investor_id, item["text"])
    #         else:
    #             _str += item["text"]
    #     else:
    #         _str += item["text"]
    # conn.close()
    # return _str
    return investorsRaw


