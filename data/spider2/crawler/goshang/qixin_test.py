# -*- coding: utf-8 -*-
import sys, os, time, datetime
import json
import requests

url_investor = 'http://api-sandbox.intsig.net/open/xiniu/venture/capital'
param = {
    "full_name":"上海合合信息科技发展有限公司",
    "short_name":"上海合合信息科技发展有限公司"
}
param1 = {

    "base" : {
            "company_name" : "上海合合信息科技发展有限公司",
            "project_logo_url" : "www.url.com",
            "project_name" : "项目例子",
            "finance_rounds" : "B",
            "website_url" : "www.intsig.net",
            "key_words" : "CC,CS,AI",
            "introduction" : "人工智能、大数据",
            "finance_info" : [
                {"date" : "2015-07-24", "round" : "天使", "amount" : "500", "currency":"人民币", "investor" : "红杉资本"},
                {"date" : "2016-07-24", "round" : "A", "amount" : "1000", "currency":"美元","investor" : "红杉资本, NDG"},
                {"date" : "2017-05-24", "round" : "B", "amount" : "5000", "currency":"美元","investor" : "红杉资本, NDG, 经纬创投"}
                ]
    },
    "team" : {
        "core_members" : [
            {"avatar_url": "http://www.member2_head_url.com", "name": "李四", "position": "CFO", "education": "北京大学学士",
             "introduction": "", "work": ""}
            ]
    },
    "competitors": [
                    {"project_name": "名称1"},
                    {"project_name": "名称2"}
    ],
    "products": [
        {"name": "名称1", "introduction": "公司产品1", "kind": "产品类型1"},
        {"name": "名称2", "introduction": "公司产品2", "kind": "产品类型2"}
    ]

}

print (param1)


res = requests.post(url_investor, data=param1)
print  res.text
# data = urllib.