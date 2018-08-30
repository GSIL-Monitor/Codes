# -*- coding: utf-8 -*-
import os, sys
from pypinyin import lazy_pinyin

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_location", stream=True)
logger = loghelper.get_logger("patch_location")

DICT = {
    u"意大利": "Italy",
    u"比利时": "Belgium",
    u"希腊": "Greece",
    u"葡萄牙": "Portugal",
    u"西班牙": "Spain",
    u"捷克": "Czech",
    u"波兰": "poland",
    u"瑞士": "Switzerland",
    u"挪威": "Norway",
    u"瑞典": "Sweden",
    u"卢森堡": "Luxembourg",
    u"乌克兰": "Ukraine",
    u"荷兰": "Netherlands",
    u"英国": "UK",
    u"丹麦": "Denmark",
    u"奥地利": "Austria",
    u"阿根廷": "Argentina",
    u"巴西": "Brazil",
    u"智利": "Chile",
    u"委内瑞拉": "Venezuela",
    u"哥伦比亚": "Columbia",
    u"乌拉圭": "Uruguay",
    u"沙特": "Saudi Arabia",
    u"马来西亚": "Malaysia",
    u"阿联酋": "The United Arab Emirates",
    u"印尼": "Indonesia",
    u"泰国": "Thailand",
    u"印度": "India",
    u"新加坡": "Singapore",
    u"韩国": "Korea",
    u"日本": "Japan",
    u"墨西哥": "Mexico",
    u"加拿大": "Canada",
    u"美国": "USA",
    u"新西兰": "New Zealand",
    u"澳大利亚": "Australia",
    u"摩洛哥": "Morocco",
    u"尼日利亚": "Nigeria",
    u"埃及": "Egypt",
    u"南非": "South Africa",
    u"德国": "Germany",
    u"法国": "France",
    u"菲律宾": "Philippines",
    u"越南": "Vietnam",
    u"俄罗斯": "Russia",
    u"芬兰": "Finland",
    u"以色列": "Israel",
    u"斯洛伐克": "Slovakia",
    u"缅甸": "Myanmar",
    u"爱尔兰": "Ireland",
    u"国外": "Outside China"
}


def main():
    conn = db.connect_torndb()
    items = conn.query("select * from location order by locationId")
    for item in items:
        location_id = item["locationId"]
        location_name = item["locationName"]
        if location_id == 0:
            location_en_name = "unknown"
        elif location_id == 340:
            location_en_name = "china"
        elif location_id < 371:
            location_en_name = "".join(lazy_pinyin(location_name))
        else:
            location_en_name = DICT.get(location_name)

        location_en_name = location_en_name.capitalize()
        logger.info("%s -> %s", location_name, location_en_name)
        conn.update("update location set locationEnName=%s where locationId=%s", location_en_name, location_id)
    conn.close()


if __name__ == "__main__":
    main()