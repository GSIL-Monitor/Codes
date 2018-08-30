insert contest(id,name,organizationId,description,startDate,endDate,status,createTime,createUser) 
values(2,'2016戈壁创投 VC Day',1,'','2016/11/23 13:00:00','2016/11/23 18:00:00',null,now(),1);

update contest set description=
'地点: 北京市朝阳区We+酒仙桥空间'
where id=2;

insert contest_topic(id,contestId,name,createTime,createUser)
values(2,2,'2016戈壁创投 VC Day',now(),1);

insert contest_stage(id,name,contestId,status,createTime,createUser)
values(2,'2016戈壁创投 VC Day',2,58010,now(),1);

insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(2,'行业',0,5,1,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(2,'团队',0,5,2,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(2,'产品',0,5,3,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(2,'盈利',0,5,4,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(2,'估值',0,5,5,now(),1);

#FellowPlus companyId=11119     pic: 5832b1104877af32c28c3048
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1111,11119,2,2,1,1,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1111,56000,now(),1);
update contest_company set contact='创始人：郭颖哲\n手机：15815561788\n微信：catdance952' 
where id=1111;
db.contest_company.insert({"contestCompanyId":1111, "contestId":2, "extra":[{"name":"picture","value":"5832b1104877af32c28c3048","type":"picture"}]})


#YeeChoo    companyId=149543    pic: 5832b1184877af32e37ac44b
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1112,149543,2,2,1,2,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1112,56000,now(),1);
update contest_company set contact='创始人：单珊\n手机：+852 9505 0881\n微信：shanshan_buding' 
where id=1112;
db.contest_company.insert({"contestCompanyId":1112, "contestId":2, "extra":[{"name":"picture","value":"5832b1184877af32e37ac44b","type":"picture"}]})
update contest_company set sort=3 where id=1112;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1112,'YeeChoo.pdf','58351f834877af238c17577c/YeeChoo.pdf',now(),1);

#Shopline   companyId=149541    pic: 5832b11d4877af32f4ea3139
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1113,149541,2,2,1,3,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1113,56000,now(),1);
update contest_company set contact='创始人：黄浩昌\n手机：+852-6746-8099\n微信：tonywongk' 
where id=1113;
db.contest_company.insert({"contestCompanyId":1113, "contestId":2, "extra":[{"name":"picture","value":"5832b11d4877af32f4ea3139","type":"picture"}]})
update contest_company set sort=6 where id=1113;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1113,'Shopline.pdf','58351f8b4877af23b5215a75/Shopline.pdf',now(),1);

#车到加油   companyId=15554      pic: 5832b1234877af330b824d8f
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1114,15554,2,2,1,4,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1114,56000,now(),1);
update contest_company set contact='创始人：肖广\n手机：13810517693\n微信：xiaoguang464726' 
where id=1114;
db.contest_company.insert({"contestCompanyId":1114, "contestId":2, "extra":[{"name":"picture","value":"5832b1234877af330b824d8f","type":"picture"}]})
update contest_company set sort=1 where id=1114;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1114,'车到加油.pdf','58351f7e4877af236551810f/车到加油.pdf',now(),1);


#魔方金服    companyId=112283      pic: 5832b1284877af332116ba61
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1115,112283,2,2,1,5,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1115,56000,now(),1);
update contest_company set contact='创始人：凌骏\n手机：18616392099\n微信：staricon' 
where id=1115;
db.contest_company.insert({"contestCompanyId":1115, "contestId":2, "extra":[{"name":"picture","value":"5832b1284877af332116ba61","type":"picture"}]})
update contest_company set sort=4 where id=1115;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1115,'魔方金服.pdf','58351f874877af239be82e9e/魔方金服.pdf',now(),1);


#奇溢自然    companyId=35054    pic: 5832b12c4877af3331aa2a6e
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1116,35054,2,2,1,6,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1116,56000,now(),1);
update contest_company set contact='创始人：左强\n手机：15021371989\n微信：15021371989' 
where id=1116;
db.contest_company.insert({"contestCompanyId":1116, "contestId":2, "extra":[{"name":"picture","value":"5832b12c4877af3331aa2a6e","type":"picture"}]})
update contest_company set sort=5 where id=1116;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1116,'奇溢自然.pdf','58352f214877af4045f4c357/奇溢自然.pdf',now(),1);


#云上会    companyId=61704     pic: 5832b1314877af334109cd7d
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1117,61704,2,2,1,7,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1117,56000,now(),1);
update contest_company set contact='创始人：张天毅\n手机：15889729931\n微信：timzhang9488894' 
where id=1117;
db.contest_company.insert({"contestCompanyId":1117, "contestId":2, "extra":[{"name":"picture","value":"5832b1314877af334109cd7d","type":"picture"}]})
update contest_company set sort=7 where id=1117;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1117,'云上会.pdf','58352f2b4877af4060c6e389/云上会.pdf',now(),1);


#皇包车    companyId=10127     pic: 5832b1364877af335c10736e
insert contest_company(id,companyId,contestId,topicId,organizationId,sort,createTime,createUser)
values(1118,10127,2,2,1,8,now(),1);
insert contest_company_stage(stageId,contestCompanyId,status,createTime,createUser)
values(2,1118,56000,now(),1);
update contest_company set contact='创始人：孟雷\n手机：18810009966\n微信：18810009966' 
where id=1118;
db.contest_company.insert({"contestCompanyId":1118, "contestId":2, "extra":[{"name":"picture","value":"5832b1364877af335c10736e","type":"picture"}]})
update contest_company set sort=2 where id=1118;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1118,'皇包车.pdf','583528214877af30c7005cd4/皇包车.pdf',now(),1);


#戈壁 1
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(152,2,1,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(152,2,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,2,'Y','N',now(),1 from user_organization_rel where organizationId=1;

#烯牛资本 51
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(153,2,51,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(153,2,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,2,'Y','N',now(),1 from user_organization_rel where organizationId=51;

#执一资本 60
#user 252, 931

#远镜创投    58  程小琳 248
#远镜创投    58  王嫣然Claire   247
#远镜创投    58  杜宇村 928


#娱乐资本论   372 杨泽华 944


#优客工场    373 马文彬 945


#英特尔投资中国区    370 王天琳 930

#毅达创投        刘晋  

#星瀚资本    167 王梓  932
#星瀚资本    167 张艾莉 933

#新天域资本   374 王昆  946
#新天域资本   374 王昆  946

#小饭桌 265 李乔  942

#五岳天下    129 周杏苑 389

#梧桐资本    387 张泽飞 963
#梧桐树资本   375 张洋  947

#无穹创投    143 李刚强 820

#天鹰资本    66  张伟哲 262

#腾讯战略    322 杨睿诗 935

#索尼中国    100 陆小睿 936
#索尼（中国）有限公司  100 潘成波 312

#尚诺集团    376 曹蕾  948

#山行资本    377 孟岩峰 

#赛富投资基金  99  周卿  937

#青桐资本    378 张艺  949

#青松基金    186 周亢  492

#乾德资本    351 曹钟匀 914

#启明创投    57  吴静  927

#企航互动    379 裴沪滨 950

#绿领资本    380 梁祎恬 951

#励石创投    179 孟繁竹 938

#蓝驰创投    80  朱俊轩 925

#宽带资本    95  欧阳琦玮    416

#经纬创投    14  林翠  281

#今日资本    81  马骏  284

#江苏苏豪一带一路资本管理有限公司    381 周磊  952

#集结号资本   369 王念卿 929

#华映资本    113 曹霞  355

#华创资本    9   曹映雪 924

#和君资本    292 崔雪源 953
#和君资本    292 魏绪  778

#国安创客学院  382 李琪  954

#贵州贵安创业投资基金管理有限公司    383 张登帅 955
#贵安创投    383 武国庆 956

#光源创投    102 张轩旗 314

#歌斐资产    31  董晓晓 939

#高通创投    106 李研  940

#方创资本    371 舒畅  943

#东方富海    384 章子麟 957
#东方富海    384 易奥  958
#东方富海    384 汤浔芳 959

#鼎盛基金    385 蔡荣春 960

#德国电信    83  陈新征 286

#晨兴资本    194 张博  926

#IDG资本   61  甄志勇 253

#GGV Capital 85  Klaus Wang  288

#DCM Ventures    386 Francis Kao 961

#1898创投  353 张腾  941

#清理打分数据
delete from contest_company_user_result where contestCompanyId in (select id from contest_company where contestId=2);
delete from contest_company_score  where contestCompanyId in (select id from contest_company where contestId=2);
update contest_company_stage set score=null where contestCompanyId in (select id from contest_company where contestId=2);



