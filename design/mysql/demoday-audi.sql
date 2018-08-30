CREATE TABLE `stage_contest_company_user_comment` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `stageId` INT NOT NULL,
  `userId` INT NOT NULL,
  `contestCompanyId` INT NOT NULL,
  `comment` TEXT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  INDEX `fk_stage_contest_company_user_comment_stage1_idx` (`stageId` ASC),
  INDEX `fk_stage_contest_company_user_comment_user1_idx` (`userId` ASC),
  PRIMARY KEY (`id`),
  INDEX `fk_stage_contest_company_user_comment_contest_company1_idx` (`contestCompanyId` ASC),
  CONSTRAINT `fk_stage_contest_company_user_comment_stage1`
    FOREIGN KEY (`stageId`)
    REFERENCES `stage` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_stage_contest_company_user_comment_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_stage_contest_company_user_comment_contest_company1`
    FOREIGN KEY (`contestCompanyId`)
    REFERENCES `contest_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table contest_company_stage add scored char(1) default 'N';

alter table stage rename contest_stage;
alter table topic rename contest_topic;

alter table contest_company_file add link varchar(500) default null after name;
alter table contest_company_file modify file varchar(100) default null;


#奥迪创新平台2016
insert contest(id,name,organizationId,description,startDate,endDate,status,createTime,createUser) 
values(10,'奥迪创新实验室2016',44,'','2016/8/12','2016/10/11',null,now(),1);

#audi: 44， 创业邦: 193，多个VC 
#戈壁创投: 1, 烯牛资本: 51

#audi
insert contest_organization(id,contestId,organizationId,createTime,createUser,joinStatus)
values(81,10,44,now(),1,57010);
#戈壁创投
insert contest_organization(id,contestId,organizationId,createTime,createUser,joinStatus)
values(82,10,1,now(),1,57010);
#烯牛资本
insert contest_organization(id,contestId,organizationId,createTime,createUser,joinStatus)
values(83,10,51,now(),1,57010);
#创业邦
insert contest_organization(id,contestId,organizationId,createTime,createUser,joinStatus)
values(84,10,193,now(),1,57010);
#一汽大众
insert contest_organization(id,contestId,organizationId,createTime,createUser,joinStatus)
values(85,10,211,now(),1,57010);

#3个主题
insert contest_topic(id,contestId,name,createTime,createUser)
values(11,10,'数字化+\nDigital+',now(),1);
insert contest_topic(id,contestId,name,createTime,createUser)
values(12,10,'车 ▪ 生活\nCar ▪ Life',now(),1);
insert contest_topic(id,contestId,name,createTime,createUser)
values(13,10,'人工智能\nAI',now(),1);

#audi三个主题
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(81,11,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(81,12,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(81,13,now(),1);
#戈壁一个主题
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(82,12,now(),1);
#烯牛三个主题
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(83,11,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(83,12,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(83,13,now(),1);
#创业邦三个主题
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(84,11,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(84,12,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(84,13,now(),1);
#一汽大众三个主题
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(85,11,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(85,12,now(),1);
insert contest_organization_topic(contestOrganizationId,topicId,createTime,createUser)
values(85,13,now(),1);


#3个轮次
insert contest_stage(id,name,contestId,status,createTime,createUser,sort)
values(11,'预选\nQualifying',10,58010,now(),1,10);
insert contest_stage(id,name,contestId,status,createTime,createUser,sort)
values(12,'联合评估\nJoint-evaluation',10,58000,now(),1,20);
insert contest_stage(id,name,contestId,status,createTime,createUser,sort)
values(13,'专场路演\nIdea Pitch',10,58000,now(),1,30);
update contest_stage set startDate='2016/8/12', endDate='2016/9/20' where id=11;
update contest_stage set startDate='2016/8/29', endDate='2016/9/28' where id=12;
update contest_stage set startDate='2016/10/9', endDate='2016/10/11' where id=13;


insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(11,11,'方案可读性\nReadability of biz plan',0,1,1,now(),1,1,'模板/格式：不清晰的，混乱的方案模板和格式导致误读\n措辞用语：过多不当的措辞用于导致误读');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(12,11,'注册信息完整度\nRegistration information complete',0,1,2,now(),1,1,'基本信息：公司基本信息不全或伪造公司基本信息\n团队信息：团队信息不全或伪造团队信息');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(13,11,'商业理念清晰度\nClear business idea',0,1,3,now(),1,1,'清晰的商业模式：清晰和有逻辑的商业理念呈现\n清晰的路线图：清晰和有逻辑的实施方案');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(14,11,'主题符合度\nTopic match',0,1,4,now(),1,1,'与主题相关：与汽车行业相关');

insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(21,12,'市场吸引力\nMarket attractiveness',1,10,1,now(),1,1,
'市场规模和趋势：市场规模，历史增长率，市场所处阶段，增长趋势
市场竞争：已有竞争对手数量，市场集中度
市场进入与发展方案：发展路线，服务可扩展性，领域可扩展性
Market size and trend: Market size; historical growth rate; market maturity; growth trend
Competitiveness of the market: # of existing players; market concentration
Development plan: Road map; service extend; area cover extend
');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(22,12,'团队背景\nTeam background',1,10,2,now(),1,1,
'团队完整度：团队规模和团队成员职能构成（技术，销售，运营，计划等）
团队能力契合度：专业（教育背景），技能（工作经验）
Completeness of team: Team size; team member\'s function (tech, sales, operation, planning)
Capability of team: Major (education); skills (working experience)');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(23,12,"与奥迪战略契合度\nMatch Audi’s strategy",1,10,3,now(),1,1,
'数字化：推动业务流程数字化，为高科技出行解决方案建立的平台
可持续化：可持续性的产品和服务（例如：新能源汽车，新生活方式衍生服务，建立新社会责任）
城市化：为城市提供能解决各类交通问题的高科技交通解决方案 （拥堵问题，停车问题等）
Digitalization: Digitalizing the process; build-up platform for high-tech mobility solutions
Sustainability: Sustainable products and services (new energy cars, new life style, new social responsibility)
Urbanization: Build up high tech traffic solutions for cities to reduce congestion, parking problem etc.');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(24,12,'产品/服务\nProduct or services',1,10,4,now(),1,1,
'价值主张：带给消费者和潜在合作伙伴的价值
盈利模式：有确定的，合理的盈利模式
Value proposition: Value brought to customers and partners
Revenue model: has logic and certain revenue model');

insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(31,13,'市场吸引力\nMarket attractiveness',1,10,1,now(),1,1,
'市场规模和趋势：市场规模，历史增长率，市场所处阶段，增长趋势
市场竞争：已有竞争对手数量，市场集中度
市场进入与发展方案：发展路线，服务可扩展性，领域可扩展性
Market size and trend: Market size; historical growth rate; market maturity; growth trend
Competitiveness of the market: # of existing players; market concentration
Development plan: Road map; service extend; area cover extend');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(32,13,'团队背景\nTeam background',1,10,2,now(),1,1,
'团队完整度：团队规模和团队成员职能构成（技术，销售，运营，计划等）
团队能力契合度：专业（教育背景），技能（工作经验）
Completeness of team: Team size; team member\'s function (tech, sales, operation, planning)
Capability of team: Major (education); skills (working experience)');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(33,13,"与奥迪战略契合度\nMatch Audi’s strategy",1,10,6,now(),1,1,
'数字化：推动业务流程数字化，为高科技出行解决方案建立的平台
可持续化：可持续性的产品和服务（例如：新能源汽车，新生活方式衍生服务，建立新社会责任）
城市化：为城市提供能解决各类交通问题的高科技交通解决方案 （拥堵问题，停车问题等）
Digitalization: Digitalizing the process; build-up platform for high-tech mobility solutions
Sustainability: Sustainable products and services (new energy cars, new life style, new social responsibility)
Urbanization: Build up high tech traffic solution for cities to reduce congestion, parking problem, etc.
');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(34,13,"产品/服务\nProduct or services",1,10,3,now(),1,1,
'价值主张：带给消费者和潜在合作伙伴的价值
渠道策略：如何接近消费者
发展方案：现覆盖地区,可拓展覆盖地区
Value proposition: Value brought to customers and partners
Distribution: How to touch customers
Development: Location covered right now; location extend.');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(35,13,'盈利模式\nProfit model',1,10,4,now(),1,1,
'收入模型：可实现的收入模式和收益增长潜力
成本模型：清晰的成本结构
投资回报率：投资回报率,内部收益率
Revenue model: Realizable income model; revenue increase potential
Cost model: Clear cost structure
ROI: ROI; IRR');
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser,weight,description)
values(36,13,'评估价值\nAssessment value',1,10,5,now(),1,1,
'以往投资
Previous investment');



#烯牛资本的用户
#insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
#select userId,11,'Y','Y',now(),1 from user_organization_rel where organizationId=51;
#insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
#select userId,12,'Y','Y',now(),1 from user_organization_rel where organizationId=51;
#insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
#select userId,13,'Y','Y',now(),1 from user_organization_rel where organizationId=51;

#audi的用户(已加)
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,11,'Y','Y',now(),1 from user_organization_rel where organizationId=44;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,12,'Y','Y',now(),1 from user_organization_rel where organizationId=44;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,13,'Y','Y',now(),1 from user_organization_rel where organizationId=44;

#戈壁的用户(未加)
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,12,'Y','Y',now(),1 from user_organization_rel where organizationId=1;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,13,'Y','N',now(),1 from user_organization_rel where organizationId=1;

#创业邦的用户(已加)
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select userId,11,'Y','Y',now(),1 from user_organization_rel where organizationId=193;

#准备第一个Stage的初始数据
#导入excel数据
#delete from contest_company_stage where stageId in (11,12,13);
#delete from contest_company_score where stageScoreDimensionId in 
#(select id from stage_score_dimension where stageId in(11,12,13));

insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select 545,11,'Y','Y',now(),1;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select 545,12,'Y','Y',now(),1;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select 545,13,'Y','Y',now(),1;

#一汽大众用户
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select 577,11,'N','N',now(),1;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select 577,12,'N','N',now(),1;
insert stage_user_rel(userId,stageId,canScore,canJudge,createTime,createUser)
select 577,13,'N','N',now(),1;

update stage_score_dimension set description=
'市场规模和趋势：市场规模，历史增长率，市场所处阶段，增长趋势
市场竞争：已有竞争对手数量，市场集中度
市场进入与发展方案：发展路线，服务可扩展性，地域可扩展性
Market size and trend: Market size; historical growth rate; market maturity; growth trend
Competitiveness of the market: # of existing players; market concentration
Development plan: Road map; service extension; geographic coverage extension
'
where id=21;

update stage_score_dimension set description=
"团队完整度：团队规模和团队成员职能构成（技术，销售，运营，计划等）
团队能力契合度：专业（教育背景），技能（工作经验）
Completeness of team: Team size; team member's function setup (tech, sales, operation, planning, etc.)
Capability of team: Major (education); skills (working experience)
"
where id=22;


update stage_score_dimension set description=
'数字化：推动业务流程数字化，为智慧出行与数字化服务构建平台
可持续化：针对产业链各环节的可持续性的产品和服务
城市化：帮助城市制定方案，缓解和减少城市中的交通问题（如拥堵、停车难等）
Digitalization: Digitalizing the process; build-up platform for connected premium mobility and digital service
Sustainability: Sustainable products and services along the whole value chain
Urbanization: Develop solutions for cities to reduce congestion, parking problem etc.
'
where id=23;

update stage_score_dimension set description=
'价值主张：带给消费者和潜在合作伙伴的价值
盈利模式：有确定的，合理的盈利模式
Value proposition: Value brought to customers and partners
Revenue model: with logical and concrete revenue model
'
where id=24;


update stage_score_dimension set description=
'市场规模和趋势：市场规模，历史增长率，市场所处阶段，增长趋势
市场竞争：已有竞争对手数量，市场集中度
市场进入与发展方案：发展路线，服务可扩展性，地域可扩展性
Market size and trend: Market size; historical growth rate; market maturity; growth trend
Competitiveness of the market: # of existing players; market concentration
Development plan: Road map; service extension; geographic coverage extension
'
where id=31;

update stage_score_dimension set description=
"团队完整度：团队规模和团队成员职能构成（技术，销售，运营，计划等）
团队能力契合度：专业（教育背景），技能（工作经验）
Completeness of team: Team size; team member's function setup (tech, sales, operation, planning etc.)
Capability of team: Major (education); skills (working experience)
"
where id=32;

update stage_score_dimension set description=
'数字化：推动业务流程数字化，为智慧出行与数字化服务构建平台
可持续化：针对产业链各环节的可持续性的产品和服务
城市化：帮助城市制定方案，缓解和减少城市中的交通问题（如拥堵、停车难等）
Digitalization: Digitalizing the process; build-up platform for connected premium mobility and digital service
Sustainability: Sustainable products and services along the whole value chain
Urbanization: Develop solutions for cities to reduce congestion, parking problem etc.
'
where id=33;

update stage_score_dimension set description=
'价值主张：带给消费者和潜在合作伙伴的价值
渠道策略：如何触达消费者
发展方案：现覆盖地区,可拓展覆盖地区
Value proposition: Value brought to customers and partners
Distribution: How to reach customers
Development: Geographic coverage right now; geographic coverage extension
'
where id=34;

update stage_score_dimension set description=
'收入模型：可实现的收入模式和收益增长潜力
成本模型：清晰的成本结构
资产回报率：资产回报率
Revenue model: Achievable income model; revenue increase potential
Cost model: Clear cost structure
Return On Capital Employed: Return On Capital Employed
'
where id=35;


update stage_score_dimension set description=
'上一轮估值
Previous valuation
', name='估值
Valuation'
where id=36;

alter table stage_score_dimension modify weight float default 1;

update stage_score_dimension set weight=6*0.20 where id=31;
update stage_score_dimension set weight=6*0.20 where id=32;
update stage_score_dimension set weight=6*0.20 where id=33;
update stage_score_dimension set weight=6*0.20 where id=34;
update stage_score_dimension set weight=6*0.15 where id=35;
update stage_score_dimension set weight=6*0.05 where id=36;