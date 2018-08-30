insert contest(id,name,organizationId,description,startDate,endDate,status,createTime,createUser) 
values(20,'IPO路演日',145,'','2016/9/6','2016/9/6',null,now(),1);

update contest set description=
'时间：2016年9月6日 13:30 ～ 16:30
地点：上海市杨浦区政学路77号INNOSPACE+一楼 IPOclub'
where id=20;


insert contest_topic(id,contestId,name,createTime,createUser)
values(20,20,'IPO路演日',now(),1);

insert contest_stage(id,name,contestId,status,createTime,createUser)
values(20,'IPO路演日',20,58010,now(),1);

insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(20,'行业',0,5,1,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(20,'团队',0,5,2,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(20,'产品',0,5,3,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(20,'盈利',0,5,4,now(),1);
insert stage_score_dimension(stageId,name,minScore,maxScore,sort,createTime,createUser)
values(20,'估值',0,5,5,now(),1);


#乐蓓 companyId=116264, file=57cd480dc8c5874540e82dff
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(115,20,116264,20,145,1,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,115,56000,now(),1);
db.contest_company.insert({"contestCompanyId":115, "contestId":20, "extra":[{"name":"picture","value":"57cd480dc8c5874540e82dff","type":"picture"}]})
update contest_company set contact='创始人：洪冬迪\n手机：13817948817\n微信：hongdongdi840106' 
where id=115;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(115,'乐蓓BP.pdf','57cd4838c8c587454e05cf02/乐蓓BP.pdf',now(),1);

#大白安心Dabaidoc companyId=134406
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(116,20,134406,20,145,2,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,116,56000,now(),1);
db.contest_company.insert({"contestCompanyId":116, "contestId":20, "extra":[{"name":"picture","value":"57cd4f99c8c58745867aab48","type":"picture"}]})
update contest_company set contact='创始人：黄茜\n手机：18121234708\n微信：kittyhq' 
where id=116;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(116,'大白安心BP.pdf','57cd4fa2c8c5874591df46d0/大白安心BP.pdf',now(),1);


#InYard
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(117,20,51405,20,145,3,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,117,56000,now(),1);
update contest_company set contact='创始人：呙芮\n手机：13512383668\n微信：364020028' 
where id=117;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(117,'InYardBP.pdf','57cd512cc8c58745d5bc77b8/InYardBP.pdf',now(),1);
db.contest_company.insert({"contestCompanyId":117, "contestId":20, 
    "extra":[{"name":"picture","value":"57cd511ec8c58745ca605413","type":"picture"}]})

#【会玩】企业活动管家
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(118,20,35758,20,145,4,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,118,56000,now(),1);
update contest_company set contact='创始人：谭晨杰 \n手机：13585911266\n微信：yizhongren1124' 
where id=118;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(118,'会玩BP.pdf','57cd528ac8c58745f3c29613/会玩BP.pdf',now(),1);
db.contest_company.insert({"contestCompanyId":118, "contestId":20, 
    "extra":[{"name":"picture","value":"57cd5293c8c5874604a13b64","type":"picture"}]})

#智慧远程康复
update company set logo='57cd5a7fc8c58746d90b85e1' where id=123761;

insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(119,20,123761,20,145,5,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,119,56000,now(),1);
update contest_company set contact='创始人：殳峰 \n手机：13661419631\n微信：fshu99' 
where id=119;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(119,'智慧远程康复BP.pdf','57cd53ddc8c587461f89c25d/智慧远程康复BP.pdf',now(),1);
db.contest_company.insert({"contestCompanyId":119, "contestId":20, 
    "extra":[{"name":"picture","value":"57cd53d4c8c5874613dd1b4c","type":"picture"}]})

#R2
update company set logo='57cd5a84c8c58746e5a85be4' where id=6805;

insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(120,20,6805,20,145,6,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,120,56000,now(),1);
update contest_company set contact='创始人：黄莹 \n手机：13918222299\n微信：hyaline2013' 
where id=120;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(120,'R2BP.pdf','57cd5517c8c58746442ffe0e/R2BP.pdf',now(),1);
db.contest_company.insert({"contestCompanyId":120, "contestId":20, 
    "extra":[{"name":"picture","value":"57cd5510c8c587463825cdc8","type":"picture"}]})

#子林的玩具
update company set logo='57cd5a8ac8c58746f119a15c' where id=20137;

insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(121,20,20137,20,145,7,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,121,56000,now(),1);
update contest_company set contact='创始人：魏泽 \n手机：18616777023\n微信：desire23' 
where id=121;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(121,'子林的玩具BP.pdf','57cd562cc8c5874665542d1e/子林的玩具BP.pdf',now(),1);
db.contest_company.insert({"contestCompanyId":121, "contestId":20, 
    "extra":[{"name":"picture","value":"57cd5634c8c5874677c95daa","type":"picture"}]})

#医基医疗
update company set logo='57cd5a91c8c58746fdefb9d2' where id=184277;

insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser)
values(122,20,184277,20,145,8,now(),1);
insert contest_company_stage(stageId, contestCompanyId,status,createTime,createUser)
values(20,122,56000,now(),1);
update contest_company set contact='创始人：李飞飞 \n手机：15821675782' 
where id=122;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(122,'医基医疗BP.pdf','57cd5718c8c587468fac9094/医基医疗BP.pdf',now(),1);
db.contest_company.insert({"contestCompanyId":122, "contestId":20, 
    "extra":[{"name":"picture","value":"57cd5721c8c587469f522f2f","type":"picture"}]})



#烯牛资本 51
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(101,20,51,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(101,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=51;


#InnoSpace 145
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(102,20,145,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(102,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','Y',now(),1 from user_organization_rel where organizationId=145;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(758,20,'Y','Y',now(),1);



#王璐君 赴港资产管理有限公司 234  424407822@qq.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(103,20,234,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(103,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=234;


#王安得 中以智教基金 235 ande.wang@cn.ey.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(104,20,235,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(104,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=235;


沈娟  创业接力天使 19  anthea_sj@163.com
陈韵  创业接力    cy@stepholdings.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(105,20,19,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(105,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=19;


尹天成 艾想投资 236   yyttcc20490@sina.com
张磊  艾想投资    kevin@ideate-investments.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(106,20,236,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(106,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=236;


茅译齐 辰海资本 237   myq@chenhaicapital.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(107,20,237,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(107,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=237;


唐栋  伯藜创投  203  13917043955@163.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(108,20,203,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(108,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=203;


朱家晨 PreAngel 125    preangel.Helen@qq.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(109,20,125,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(109,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(547,20,'Y','N',now(),1);


欧小文 灏源资本  238  ouxiaowen@hyzb.co
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(110,20,238,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(110,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=238;


楼群  戈壁创投  1  bill@gobivc.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(111,20,1,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(111,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(5,20,'Y','N',now(),1);


stella  光速中国 163   494807885@qq.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(112,20,163,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(112,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(519,20,'Y','N',now(),1);


邢文芳 英诺天使基金 27 xingwenfang@innoangel.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(113,20,27,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(113,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(149,20,'Y','N',now(),1);

江子骞 汇付创投  239  jzq@pnrvc.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(114,20,239,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(114,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=239;


余熹  洪泰基金  32  Yuxi@angelplus.cn
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(115,20,32,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(115,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(227,20,'Y','N',now(),1);


翁博涵 联升创投  241  wbh@atlas-venture.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(116,20,241,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(116,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=241;


王嘉凌 真格基金  12  angela@zhenfund.com
姚旭雯 真格基金    xuwen@zhenfund.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(117,20,12,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(117,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(648,20,'Y','N',now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
values(649,20,'Y','N',now(),1);


李凌  毅园创投  158  JLEE@egardenvc.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(118,20,158,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(118,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=158;

王冰  车创投资  242  laoshen69@aliyun.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(119,20,242,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(119,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=242;


陈俊兵 天奇阿米巴  243 hi@skycheeclub.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(120,20,243,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(120,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=243;

昝桐  八百金控  244  172419221@qq.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(121,20,244,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(121,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=244;

孙捷  太冠资本   245 sunsoccer@163.com
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(122,20,245,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(122,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=245;

刘临  海天会 247 larryliu@zzgroup.co
insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(123,20,247,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(123,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=247;



insert contest_organization(id, contestId,organizationId,createTime,createUser,joinStatus)
values(124,20,252,now(),1,57010);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(124,20,now(),1);
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,20,'Y','N',now(),1 from user_organization_rel where organizationId=252;


#清理打分数据
115,116,117,118,119,120,121,122
delete from contest_company_user_result where contestCompanyId in (115,116,117,118,119,120,121,122);
delete from contest_company_score  where contestCompanyId in (115,116,117,118,119,120,121,122);
update contest_company_stage set score=null where contestCompanyId in (115,116,117,118,119,120,121,122);


