-- -----------------------------------------------------
-- Table `contest`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(500) NOT NULL,
  `organizationId` INT NOT NULL,
  `description` TEXT NULL,
  `startDate` DATETIME NULL,
  `endDate` DATETIME NULL,
  `status` INT NULL,
  `active` CHAR(1) NULL DEFAULT 'Y',
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_contest_organization1_idx` (`organizationId` ASC),
  CONSTRAINT `fk_contest_organization1`
    FOREIGN KEY (`organizationId`)
    REFERENCES `organization` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `topic`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `topic` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestId` INT NOT NULL,
  `name` VARCHAR(500) NULL,
  `active` CHAR(1) NULL DEFAULT 'Y',
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_topic_contest1_idx` (`contestId` ASC),
  CONSTRAINT `fk_topic_contest1`
    FOREIGN KEY (`contestId`)
    REFERENCES `contest` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `contest_company`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_company` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestId` INT NOT NULL,
  `companyId` INT NOT NULL,
  `topicId` INT NOT NULL,
  `organizationId` INT NULL,
  `name` VARCHAR(500) NULL,
  `round` INT NULL,
  `location` VARCHAR(100) NULL,
  `brief` TEXT NULL,
  `fundedDate` DATETIME NULL,
  `teamSize` INT NULL,
  `company` TEXT NULL,
  `joinStatus` INT NULL,
  `sort` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `source` INT NULL,
  `sourceId` VARCHAR(100) NULL,
  `extra` TEXT NULL,
  `contact` TEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_demoday_company_company1_idx` (`companyId` ASC),
  INDEX `fk_demoday_company_organization1_idx` (`organizationId` ASC),
  INDEX `fk_demoday_company_topic1_idx` (`topicId` ASC),
  INDEX `fk_contest_company_contest1_idx` (`contestId` ASC),
  CONSTRAINT `fk_demoday_company_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_demoday_company_organization1`
    FOREIGN KEY (`organizationId`)
    REFERENCES `organization` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_demoday_company_topic1`
    FOREIGN KEY (`topicId`)
    REFERENCES `topic` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contest_company_contest1`
    FOREIGN KEY (`contestId`)
    REFERENCES `contest` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


-- -----------------------------------------------------
-- Table `contest_organization`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_organization` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestId` INT NOT NULL,
  `organizationId` INT NOT NULL,
  `role` INT NOT NULL,
  `joinStatus` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_contest_organization_organization1_idx` (`organizationId` ASC),
  INDEX `fk_contest_organization_contest1_idx` (`contestId` ASC),
  UNIQUE INDEX `uq_contest_organization_contestId_organizationId` (`organizationId` ASC, `contestId` ASC),
  CONSTRAINT `fk_contest_organization_organization1`
    FOREIGN KEY (`organizationId`)
    REFERENCES `organization` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contest_organization_contest1`
    FOREIGN KEY (`contestId`)
    REFERENCES `contest` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `stage`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `stage` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(500) NULL,
  `contestId` INT NOT NULL,
  `description` TEXT NULL,
  `sort` INT NOT NULL,
  `type` INT NULL,
  `status` INT NULL,
  `nextNum` INT NULL,
  `startDate` DATETIME NULL,
  `endDate` DATETIME NULL,
  `showNext` CHAR(1) NULL DEFAULT 'Y',
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_stage_contest1_idx` (`contestId` ASC),
  CONSTRAINT `fk_stage_contest1`
    FOREIGN KEY (`contestId`)
    REFERENCES `contest` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `stage_score_dimension`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `stage_score_dimension` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `stageId` INT NOT NULL,
  `name` VARCHAR(500) NULL,
  `description` TEXT NULL,
  `weight` INT NULL,
  `minScore` INT NULL,
  `maxScore` INT NULL,
  `modifyUser` INT NULL,
  `sort` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_dimension_expand_contest_stage1_idx` (`stageId` ASC),
  CONSTRAINT `fk_dimension_expand_contest_stage1`
    FOREIGN KEY (`stageId`)
    REFERENCES `stage` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `contest_company_score`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_company_score` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestCompanyId` INT NOT NULL,
  `stageScoreDimensionId` INT NOT NULL,
  `userId` INT NOT NULL,
  `score` INT NULL,
  `reason` TEXT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_contest_stage_score_user1_idx` (`userId` ASC),
  INDEX `fk_contest_stage_score_contest_company1_idx` (`contestCompanyId` ASC),
  INDEX `fk_contest_stage_score_stage_score_dimension1_idx` (`stageScoreDimensionId` ASC),
  UNIQUE INDEX `unq_content_company_score1` (`contestCompanyId` ASC, `stageScoreDimensionId` ASC, `userId` ASC),
  CONSTRAINT `fk_contest_stage_score_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contest_stage_score_contest_company1`
    FOREIGN KEY (`contestCompanyId`)
    REFERENCES `contest_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contest_stage_score_stage_score_dimension1`
    FOREIGN KEY (`stageScoreDimensionId`)
    REFERENCES `stage_score_dimension` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `contest_company_stage`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_company_stage` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `stageId` INT NOT NULL,
  `contestCompanyId` INT NOT NULL,
  `score` FLOAT NULL,
  `status` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_state_company_stage1_idx` (`stageId` ASC),
  INDEX `fk_state_company_contest_company1_idx` (`contestCompanyId` ASC),
  UNIQUE INDEX `unq_content_company_stage1` (`stageId` ASC, `contestCompanyId` ASC),
  CONSTRAINT `fk_state_company_stage1`
    FOREIGN KEY (`stageId`)
    REFERENCES `stage` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_state_company_contest_company1`
    FOREIGN KEY (`contestCompanyId`)
    REFERENCES `contest_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `stage_user_rel`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `stage_user_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `stageId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `canScore` CHAR(1) NULL,
  `canJudge` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_stage_user_rel_user1_idx` (`userId` ASC),
  INDEX `fk_stage_user_rel_stage1_idx` (`stageId` ASC),
  CONSTRAINT `fk_stage_user_rel_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_stage_user_rel_stage1`
    FOREIGN KEY (`stageId`)
    REFERENCES `stage` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `contest_organization_topic`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_organization_topic` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestOrganizationId` INT NOT NULL,
  `topicId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_content_organization_topic_contest_organization1_idx` (`contestOrganizationId` ASC),
  INDEX `fk_content_organization_topic_topic1_idx` (`topicId` ASC),
  CONSTRAINT `fk_content_organization_topic_contest_organization1`
    FOREIGN KEY (`contestOrganizationId`)
    REFERENCES `contest_organization` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_content_organization_topic_topic1`
    FOREIGN KEY (`topicId`)
    REFERENCES `topic` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `contest_company_file`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_company_file` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestCompanyId` INT NOT NULL,
  `name` VARCHAR(500) NOT NULL,
  `file` VARCHAR(100) NOT NULL,
  `createTime` DATETIME NULL,
  `modifyTime` DATETIME NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_contest_company_file_contest_company1_idx` (`contestCompanyId` ASC),
  CONSTRAINT `fk_contest_company_file_contest_company1`
    FOREIGN KEY (`contestCompanyId`)
    REFERENCES `contest_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `contest_company_user_result`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_company_user_result` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestCompanyId` INT NOT NULL,
  `userId` INT NOT NULL,
  `result` INT NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_contest_company_user_rel_contest_company1_idx` (`contestCompanyId` ASC),
  INDEX `fk_contest_company_user_rel_user1_idx` (`userId` ASC),
  INDEX `uq_contest_company_user_result_userId_contestCompanyId` (`contestCompanyId` ASC, `userId` ASC),
  CONSTRAINT `fk_contest_company_user_rel_contest_company1`
    FOREIGN KEY (`contestCompanyId`)
    REFERENCES `contest_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contest_company_user_rel_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `contest_company_organization_result`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `contest_company_organization_result` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `contestCompanyId` INT NOT NULL,
  `organizationId` INT NOT NULL,
  `result` INT NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_contest_company_organization_result_contest_company1_idx` (`contestCompanyId` ASC),
  INDEX `fk_contest_company_organization_result_organization1_idx` (`organizationId` ASC),
  UNIQUE INDEX `uq_contest_compamy_org_result_orgId_contestCompayId` (`organizationId` ASC, `contestCompanyId` ASC),
  CONSTRAINT `fk_contest_company_organization_result_contest_company1`
    FOREIGN KEY (`contestCompanyId`)
    REFERENCES `contest_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_contest_company_organization_result_organization1`
    FOREIGN KEY (`organizationId`)
    REFERENCES `organization` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



insert contest(id,name,organizationId,description,startDate,endDate,status,createTime,createUser) 
values(1,'2016戈壁创投 VC Day',1,'','2016/7/20','2016/7/20',null,now(),1);

insert contest_organization(contestId,organizationId,createTime,createUser,joinStatus)
values(1,1,now(),1,28030);

insert topic(id,contestId,name,createTime,createUser)
values(1,1,'2016戈壁创投 VC Day',now(),1);

#金韬新能源 companyId=57146, file=578b566de4861d6738cc6948, logo=578b5b3fe4861d04eb025037
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(1,1,57146,1,1,1,now(),1,'[{"name":"picture","value":"578b566de4861d6738cc6948","type":"picture"}]');
update company set logo='578b5b3fe4861d04eb025037' where id=57146;
update contest_company set contact='创始人：张大伟\n手机：18621900826\n微信：destop001' where id=1;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(1,'金韬新能源BP.pdf','578f02dae4861d5caf543957/金韬新能源BP.pdf',now(),1);


#优购汽车  companyId=53473, file=578b570ee4861d6ad00c268b, logo=578b5b64e4861d05c36b2768
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(2,1,53473,1,1,2,now(),1,'[{"name":"picture","value":"578b570ee4861d6ad00c268b","type":"picture"}]');
update company set logo='578b5b64e4861d05c36b2768' where id=53473;
update contest_company set contact='创始人：赵卿\n手机：13920576300\n微信：rodgerzhao' where id=2;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(2,'优购汽车BP.pdf','578f1196e4861d642ac824e4/优购汽车BP.pdf',now(),1);

#全州印象 companyId=52241, file=578b575be4861d6cba885306, logo=578b5b80e4861d068b859044
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(3,1,52241,1,1,3,now(),1,'[{"name":"picture","value":"578b575be4861d6cba885306","type":"picture"}]');
update company set logo='578b5b80e4861d068b859044' where id=52241;
update contest_company set contact='创始人：李乃旭\n手机：15001283800\n微信：nathanli1027' where id=3;

insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(3,'全州印象BP.pdf','578f1638e4861d64dd9d7be8/全州印象BP.pdf',now(),1);


#游多多  companyId=3175, file=578ddf38e4861d1eb54ae4d6, logo=578b5b98e4861d06f57bad82
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(4,1,3175,1,1,4,now(),1,'[{"name":"picture","value":"578cc5f4e4861d1eb8d106e3","type":"picture"}]');
update company set logo='578b5b98e4861d06f57bad82' where id=3175;
update contest_company set contact='创始人：苗湾儿\n手机：13817731827\n微信：marriane' where id=4;
update contest_company set extra='[{"name":"picture","value":"578ddf38e4861d1eb54ae4d6","type":"picture"}]' where id=4;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(4,'游多多.pdf','578f118ce4861d64197434f9/游多多.pdf',now(),1);


#维C理财 companyId=19461, file=578b5791e4861d6dfb3be8ed, logo=578b5bafe4861d07c57f7fa1
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(5,1,19461,1,1,5,now(),1,'[{"name":"picture","value":"578b5791e4861d6dfb3be8ed","type":"picture"}]');
update company set logo='578b5bafe4861d07c57f7fa1' where id=19461;
update contest_company set contact='创始人：薛俊龙\n手机：18088888873\n微信：Jackie_pku' where id=5;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(5,'维C理财BP.pdf','578f0713e4861d62d1b0f839/维C理财BP.pdf',now(),1);

#随手攒 companyId=43944, file=578cc5fce4861d1ec4b68255, logo=578b5c7fe4861d0c9b714f79
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(6,1,43944,1,1,6,now(),1,'[{"name":"picture","value":"578cc5fce4861d1ec4b68255","type":"picture"}]');
update company set logo='578b5c7fe4861d0c9b714f79' where id=43944;
update contest_company set contact='创始人：姚铁兵\n手机：13811558673\n微信：yaotiebing' where id=6;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(6,'随手攒BP.pdf','578f0966e4861d630bbac759/随手攒BP.pdf',now(),1);

#隐食纪 companyId=137812, file=578b57c5e4861d6f55d9d2ab, logo=578b5c96e4861d0d1db2242c
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(7,1,137812,1,1,7,now(),1,'[{"name":"picture","value":"578b57c5e4861d6f55d9d2ab","type":"picture"}]');
update company set logo='578b5c96e4861d0d1db2242c' where id=137812;
update contest_company set contact='创始人：吴皓\n手机：18551839082\n微信：line0wuhao' where id=7;
insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(7,'隐食纪BP.pdf','578f1179e4861d63f7c9100b/隐食纪BP.pdf',now(),1);

#魔方天空 companyId=1687, file=578cc5e9e4861d1eadd44b9a, logo=578b5cb0e4861d0d82bc2a54
insert contest_company(id,contestId,companyId,topicId,organizationId,sort,createTime,createUser,extra)
values(8,1,1687,1,1,8,now(),1,'[{"name":"picture","value":"578cc5e9e4861d1eadd44b9a","type":"picture"}]');
update company set logo='578b5cb0e4861d0d82bc2a54' where id=1687;
update contest_company set contact='创始人：张征\n手机：13910010119\n微信：Nivalgavin' where id=8;

insert contest_company_file(contestCompanyId,name,file,createTime,createUser)
values(8,'魔方天空.pdf','578f1183e4861d6408f865f8/魔方天空.pdf',now(),1);

insert stage(id,name,contestId,status,createTime,createUser)
values(1,'2016戈壁创投 VC Day',1,54010,now(),1);

insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser)
values(1,1,'行业',0,5,1,now(),1);
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser)
values(2,1,'团队',0,5,2,now(),1);
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser)
values(3,1,'产品',0,5,3,now(),1);
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser)
values(4,1,'盈利',0,5,4,now(),1);
insert stage_score_dimension(id,stageId,name,minScore,maxScore,sort,createTime,createUser)
values(5,1,'估值',0,5,5,now(),1);


insert stage_user_rel(userId,stageId,canScore,createTime,createUser)
select id,1,'Y',now(),1 from user where email like '%@gobivc.com';

insert contest_organization(contestId,organizationId,createTime,createUser,joinStatus)
values(1,51,now(),1,28030);

insert stage_user_rel(userId,stageId,canScore,createTime,createUser)
select id,1,'Y',now(),1 from user where email like '%@xiniudata.com';

#金韬新能源
update contest_company set sort=1 where companyId=57146;
#隐食纪
update contest_company set sort=2 where companyId=137812;
#维C理财
update contest_company set sort=3 where companyId=19461;
#全州印象
update contest_company set sort=4 where companyId=52241;
#魔方天空 companyId=1687
update contest_company set sort=5 where companyId=1687;
#优购汽车  companyId=53473
update contest_company set sort=6 where companyId=53473;
#随手攒 companyId=43944
update contest_company set sort=7 where companyId=43944;
#游多多  companyId=3175
update contest_company set sort=8 where companyId=3175;


insert contest_organization(contestId,organizationId,createTime,createUser,joinStatus)
select distinct 1,r.organizationId,now(),1,28030 from user_organization_rel r join user u on r.userId=u.id where email in 
('Kang@qimingvc.com',
'Stella@qimingvc.com',
'duqian@trvc.com.cn',
'jinge@trvc.com.cn',
'wangyanran@trvc.com.cn',
'chengxiaolin@trvc.com.cn',
'yueyu@cgcvc.com',
'liyha@legendholdings.com.cn',
'xiecx@yicapital.com',
'wangl@zhiyivc.com',
'jason_zhen@idgvc.com',
'Yiting_xu@idgvc.com',
'bowen@zhenfund.com',
'justin@zhenfund.com',
'kerui@yuanshengcapital.com',
'Allen.Zhu@NokiaGrowthPartners.com',
'Simon.zhang@nokiagrowthpartners.com',
'18510147178@163.com',
'ellencheng@me.com',
'Jeff.zhang@yingcapital.com',
'zhaonan@vertexmgt.com',
'bob@tsingcapital.com',
'Xlhou@sbcvc.com',
'ninan.zhang@139.com',
'cdl@future-cap.com',
'2311972098@qq.com',
'diva@scapitol.com',
'zhang_yan@lakala.com',
'Nan.lv@sig.com',
'chenyunfei@rivervc.com',
'linyw08@hotmail.com',
'summertang@zero2ipo.com.cn',
'jennysha@zero2ipo.com.cn',
'liuhn08@hotmail.com',
'ashi@sbaif.com',
'leyna.li@cdhfund.com',
'daishuai.ds@alibaba-inc.com',
'nina.wang@pandavcfund.com',
'xujh@yonghuacapital.com.cn',
'xiansj@yonghuacapital.com.cn',
'wangzhuangzhi@fortunevc.com',
'shitingna@pinetreecapital.cn',
'claire.lin@matrixpartners.com.cn',
'fhu@brv.com.cn',
'gzhou@redpoint.com',
'majun@capitaltoday.com',
'shenwenchao@chuangxin.com',
'caroline.chen@telekom.com',
'haoyu.li@nlvc.com',
'kwang@ggvc.com',
'Xiandong@k2vc.com',
'tzhou@spd-svbank.com',
'wull@fosun.com',
'eric.shen@126.com',
'guanyingying@lmfvc.com',
'shaun@gsrventures.com',
'wangyi@jdcapital.com',
'leonard_zeng@great-capital.com',
'bruce.yang@jd.com',
'jiangzhifan1@jd.com',
'fenghuagang1@jd.com',
'Xiaodi1@jd.com',
'jinhaiyan@apluscap.com',
'Zhen.xu@cathay.fr',
'lianshufan@gmail.com',
'yzhang@bluelakecap.com',
'xiaoyb@pinevc.com.cn',
'zyw@pansheng.com.cn',
'zsc@pansheng.com',
'voler@qq.com');


insert stage_user_rel(userId,stageId,canScore,createTime,createUser)
select id,1,'Y',now(),1 from user where email in ('Kang@qimingvc.com',
'Stella@qimingvc.com',
'duqian@trvc.com.cn',
'jinge@trvc.com.cn',
'wangyanran@trvc.com.cn',
'chengxiaolin@trvc.com.cn',
'yueyu@cgcvc.com',
'liyha@legendholdings.com.cn',
'xiecx@yicapital.com',
'wangl@zhiyivc.com',
'jason_zhen@idgvc.com',
'Yiting_xu@idgvc.com',
'bowen@zhenfund.com',
'justin@zhenfund.com',
'kerui@yuanshengcapital.com',
'Allen.Zhu@NokiaGrowthPartners.com',
'Simon.zhang@nokiagrowthpartners.com',
'18510147178@163.com',
'ellencheng@me.com',
'Jeff.zhang@yingcapital.com',
'zhaonan@vertexmgt.com',
'bob@tsingcapital.com',
'Xlhou@sbcvc.com',
'ninan.zhang@139.com',
'cdl@future-cap.com',
'2311972098@qq.com',
'diva@scapitol.com',
'zhang_yan@lakala.com',
'Nan.lv@sig.com',
'chenyunfei@rivervc.com',
'linyw08@hotmail.com',
'summertang@zero2ipo.com.cn',
'jennysha@zero2ipo.com.cn',
'liuhn08@hotmail.com',
'ashi@sbaif.com',
'leyna.li@cdhfund.com',
'daishuai.ds@alibaba-inc.com',
'nina.wang@pandavcfund.com',
'xujh@yonghuacapital.com.cn',
'xiansj@yonghuacapital.com.cn',
'wangzhuangzhi@fortunevc.com',
'shitingna@pinetreecapital.cn',
'claire.lin@matrixpartners.com.cn',
'fhu@brv.com.cn',
'gzhou@redpoint.com',
'majun@capitaltoday.com',
'shenwenchao@chuangxin.com',
'caroline.chen@telekom.com',
'haoyu.li@nlvc.com',
'kwang@ggvc.com',
'Xiandong@k2vc.com',
'tzhou@spd-svbank.com',
'wull@fosun.com',
'eric.shen@126.com',
'guanyingying@lmfvc.com',
'shaun@gsrventures.com',
'wangyi@jdcapital.com',
'leonard_zeng@great-capital.com',
'bruce.yang@jd.com',
'jiangzhifan1@jd.com',
'fenghuagang1@jd.com',
'Xiaodi1@jd.com',
'jinhaiyan@apluscap.com',
'Zhen.xu@cathay.fr',
'lianshufan@gmail.com',
'yzhang@bluelakecap.com',
'xiaoyb@pinevc.com.cn',
'zyw@pansheng.com.cn',
'zsc@pansheng.com',
'voler@qq.com');


update organization set grade=33020 where id>1;


insert contest_organization(contestId,organizationId,createTime,createUser,joinStatus)
select distinct 1,r.organizationId,now(),1,28030 from user_organization_rel r join user u on r.userId=u.id where email in 
('j-zhudi@360.cn');


insert stage_user_rel(userId,stageId,canScore,createTime,createUser)
select id,1,'Y',now(),1 from user where email in 
('j-zhudi@360.cn');


