insert contest(id,name,organizationId,description,startDate,endDate,status,createTime,createUser) 
values(30,'IPO路演日',145,'','2016/10/18','2016/10/18',null,now(),1);

update contest set description=
'时间：2016年10月18日 13:30 ～ 16:30
地点：上海市杨浦区政学路77号INNOSPACE+一楼 IPOclub'
where id=30;


insert contest_topic(id,contestId,name,createTime,createUser)
values(30,30,'IPO路演日',now(),1);

insert contest_stage(id,name,contestId,status,createTime,createUser)
values(30,'IPO路演日',30,58010,now(),1);

insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(30,'行业',0,5,1,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(30,'团队',0,5,2,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(30,'产品',0,5,3,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(30,'盈利',0,5,4,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(30,'估值',0,5,5,now(),1);


#ELZA幻装 companyId=48602  pic: 58031d78c8c5876beda7b56d  bp: 58031e99c8c5876c47510afc
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1101,30,48602,30,145,1,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1101,56000,now(),1);
update contest_company set contact='创始人：冯缨茹\n手机：15800895263\n微信：fengyingru' 
where id=1101;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1101,'ELZA幻装.pdf','58031e99c8c5876c47510afc/ELZA幻装.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1101, "contestId":30, "extra":[{"name":"picture","value":"58031d78c8c5876beda7b56d","type":"picture"}]})


#neta  neta0122   115856    pic: 58031f87c8c5876c7dd37f64  bp: 58031f92c8c5876c884f79e6
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1102,30,115856,30,145,1,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1102,56000,now(),1);
update contest_company set contact='创始人：许斐\n手机：13817888070\n微信：13817888070' 
where id=1102;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1102,'neta.pdf','58031f92c8c5876c884f79e6/neta.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1102, "contestId":30, "extra":[{"name":"picture","value":"58031f87c8c5876c7dd37f64","type":"picture"}]})


#一堂好课 zhongfenjiaoyu 33302     pic: 58031f9cc8c5876c9981adf4  bp: 58031fa8c8c5876ca59e0c37
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1103,30,33302,30,145,1,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1103,56000,now(),1);
update contest_company set contact='创始人：于威\n手机：18688898306\n微信：18688898306' 
where id=1103;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1103,'一堂好课.pdf','58031fa8c8c5876ca59e0c37/一堂好课.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1103, "contestId":30, "extra":[{"name":"picture","value":"58031f9cc8c5876c9981adf4","type":"picture"}]})

#云植科技 麻麻汇 yunzhikeji13 188805   pic: 58031fb5c8c5876cb40d6209  bp: 58031fbdc8c5876cbf286cd4
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1104,30,188805,30,145,4,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1104,56000,now(),1);
update contest_company set contact='创始人：吉鹏\n手机：13911903517\n微信：peng13911903517' 
where id=1104;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1104,'云植科技.pdf','58031fbdc8c5876cbf286cd4/云植科技.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1104, "contestId":30, "extra":[{"name":"picture","value":"58031fb5c8c5876cb40d6209","type":"picture"}]})


#出发吧 chufaba 2396   pic: 58031fc2c8c5876cd04634ef  bp: 58031fc8c8c5876cdcf79455
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1105,30,2396,30,145,5,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1105,56000,now(),1);
update contest_company set contact='创始人：张辛欣\n手机：18621061452\n微信：kenzo22' 
where id=1105;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1105,'出发吧.pdf','58031fc8c8c5876cdcf79455/出发吧.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1105, "contestId":30, "extra":[{"name":"picture","value":"58031fc2c8c5876cd04634ef","type":"picture"}]})


#快玩我 mohe 144843    pic: 58031fcec8c5876ced0ca7ae  bp: 58031fd4c8c5876cf8125dd2
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1106,30,144843,30,145,6,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1106,56000,now(),1);
update contest_company set contact='创始人：陈祺\n手机：15990099918\n微信：185118' 
where id=1106;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1106,'快玩我.pdf','58031fd4c8c5876cf8125dd2/快玩我.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1106, "contestId":30, "extra":[{"name":"picture","value":"58031fcec8c5876ced0ca7ae","type":"picture"}]})

#毕业梦 VKMIOHP3 188801    pic: 58031fddc8c5876d1514677a  bp: 58031fe4c8c5876d2172316d
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1107,30,188801,30,145,6,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1107,56000,now(),1);
update contest_company set contact='创始人：祝挺\n手机：18221408730\n微信：18221408730' 
where id=1107;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1107,'毕业梦.pdf','58031fe4c8c5876d2172316d/毕业梦.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1107, "contestId":30, "extra":[{"name":"picture","value":"58031fddc8c5876d1514677a","type":"picture"}]})


#狗管家 tutawangluo 9813   pic: 58031febc8c5876d3438a2e7  bp: 58031ff1c8c5876d40e34503
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1108,30,9813,30,145,8,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1108,56000,now(),1);
update contest_company set contact='创始人：孙立\n手机：13361822615' 
where id=1108;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1108,'狗管家.pdf','58031ff1c8c5876d40e34503/狗管家.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1108, "contestId":30, "extra":[{"name":"picture","value":"58031febc8c5876d3438a2e7","type":"picture"}]})

#闲画部落 RMOOQHT4 153507   pic: 58031ff8c8c5876d520e5ddf  bp: 58031fffc8c5876d5ed51085
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(1109,30,153507,30,145,9,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(30,1109,56000,now(),1);
update contest_company set contact='创始人：周盛熙\n手机：13816696158\n微信：13816696158' 
where id=1109;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1109,'闲画部落.pdf','58031fffc8c5876d5ed51085/闲画部落.pdf',now(),1);

db.contest_company.insert({"contestCompanyId":1109, "contestId":30, "extra":[{"name":"picture","value":"58031ff8c8c5876d520e5ddf","type":"picture"}]})



#烯牛资本 51
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(125,30,51,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(125,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where organizationId=51;


#InnoSpace 145
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(126,30,145,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(126,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','Y',now(),1 from user_organization_rel where organizationId=145;


#艾想投资    236
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(127,30,236,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(127,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=236;

#八百金控    244
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(128,30,244,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(128,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=244;

#晨晖创投    121
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(129,30,121,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(129,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=121;

#赴港资产    234
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(130,30,234,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(130,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=234;

#灏源资本    238
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(131,30,238,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(131,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=238;

#洪泰基金    32
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(132,30,32,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(132,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=32;

#汇付创投    304
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(133,30,304,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(133,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=304;


#尖晶资本    305
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(134,30,305,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(134,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=305;


#江苏苏大天宫创业投资管理有限公司    306
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(135,30,306,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(135,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=306;

#爵泰资本    296
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(136,30,296,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(136,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=296;

#联通创投    302
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(137,30,302,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(137,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=302;

#摩根大通    299
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(138,30,299,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(138,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=299;

#青松基金    186
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(139,30,186,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(139,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=186;

#荣客资产    300
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(140,30,300,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(140,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=300;

#上海易津投资股份有限公司    303
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(141,30,303,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(141,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=303;

#天奇阿米巴   243
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(142,30,243,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(142,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=243;

#协立投资    297
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(143,30,297,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(143,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=297;

#雅胜投资    294
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(144,30,294,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(144,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=294;

#真格基金    12
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(145,30,12,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(145,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=12;

#致达投资    301
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(146,30,301,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(146,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=301;
    
#中贤资本    295
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(147,30,295,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(147,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=295;

#中以智教基金  235
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(148,30,235,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(148,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=235;

#Cocoon Networks 308
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(149,30,308,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(149,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=308;

#行早创投 309
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(150,30,309,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(150,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where 
organizationId=309;


#戈壁资本 1
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(151,30,1,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(151,30,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,30,'Y','N',now(),1 from user_organization_rel where organizationId=1;

#清理打分数据
delete from contest_company_user_result where contestCompanyId in (select id from contest_company where contestId=30);
delete from contest_company_score  where contestCompanyId in (select id from contest_company where contestId=30);
update contest_company_stage set score=null where contestCompanyId in (select id from contest_company where contestId=30);


