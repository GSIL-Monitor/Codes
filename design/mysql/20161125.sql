CREATE TABLE IF NOT EXISTS `tsb_v2`.`user_investor_apply` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `name` VARCHAR(100) NULL,
  `orgName` VARCHAR(200) NULL,
  `position` INT NULL,
  `email` VARCHAR(100) NULL,
  `phone` VARCHAR(100) NULL,
  `namecard` VARCHAR(50) NULL,
  `createTime` TIMESTAMP NULL,
  `auditor` INT NULL,
  `auditTime` TIMESTAMP NULL,
  `auditResult` CHAR(1) NULL,
  `migration` CHAR(1) NULL,
  `migrateTime` CHAR(1) NULL,
  INDEX `fk_table1_user1_idx` (`userId` ASC),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_table1_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `tsb_v2`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`user_default_company_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `companyId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_user_default_company_rel_user1_idx` (`userId` ASC),
  INDEX `fk_user_default_company_rel_company1_idx` (`companyId` ASC),
  UNIQUE INDEX `fk_udcr_unq` (`userId` ASC, `companyId` ASC),
  CONSTRAINT `fk_user_default_company_rel_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `tsb_v2`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_user_default_company_rel_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`sms` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `phone` VARCHAR(50) NULL,
  `code` VARCHAR(10) NULL,
  `createTime` TIMESTAMP NULL,
  `type` INT NULL,
  `sent` CHAR(1) NULL,
  `sendTime` TIMESTAMP NULL,
  `sendFailCount` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


alter table user add userIdentify int default null;
alter table user add phoneVerify char(1) default null;
alter table user add position varchar(100) default null;
alter table organization add serviceEndDate Datetime default null;
alter table organization add trial char(1) default null;
alter table user add verifiedInvestor char(1) default null;

select count(*) from deal_user_score s join deal d on d.id=s.dealId where score=4;
select userId,dealId,count(*) cnt from deal_user_score s join deal d on d.id=s.dealId where score=4 group by userId,dealId having cnt>1;
insert user_default_company_rel(userId,companyId,createTime) 
  select s.userId,d.companyId,s.createTime from deal_user_score s join deal d on d.id=s.dealId 
  where score=4 order by s.createTime;

alter table location add areacode varchar(10) default null;
alter table location add zipcode varchar(10) default null;
alter table source_company add aggregateGrade int default null;

alter table organization add emailDomain varchar(100) default null;
alter table user_organization_rel add trial char(1) default null;
alter table user_organization_rel add serviceEndDate Datetime default null;
alter table user_organization_rel add trailCount int default 0;
alter table user_organization_rel add active char(1) default null;
alter table user_investor_apply add emailDomain varchar(100) default null;
alter table user_investor_apply drop migration;
alter table user_investor_apply drop migrateTime;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`user_enterprise_trial_apply` (
  `id` INT NOT NULL,
  `useId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  `processStatus` CHAR(1) NULL,
  `processTime` TIMESTAMP NULL,
  `approveStatus` CHAR(1) NULL,
  `approveDesc` TEXT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_user_enterprise_trial_apply_user1_idx` (`useId` ASC),
  CONSTRAINT `fk_user_enterprise_trial_apply_user1`
    FOREIGN KEY (`useId`)
    REFERENCES `tsb_v2`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


--新用户null, 未认证老用户O, 已认证Y
alter table user add emailVerify char(1) default null;
alter table user add emailVerifyCode varchar(10) default null;
alter table user add emailVerifyTime datetime default null;

--发布时要更新数据
update user set emailVerify='O';
update user set phoneVerify='O' where phone is not null and phone!="";


CREATE TABLE IF NOT EXISTS `tsb_v2`.`email_task` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(50) NULL,
  `code` VARCHAR(10) NULL,
  `createTime` TIMESTAMP NULL,
  `type` INT NULL,
  `sent` CHAR(1) NULL,
  `sendTime` TIMESTAMP NULL,
  `sendFailCount` INT NULL,
  `codeUsed` CHAR(1) NULL,
  `codeUsedTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

alter table sms add `codeUsed` CHAR(1) NULL;
alter table sms add `codeUsedTime` TIMESTAMP NULL;

alter table collection add onlyForInvestor char(1) default null;

alter table user_wechat add type int default 1;
alter table user_wechat add unionId varchar(100);
alter table user drop key email;
alter table user add index(email);
alter table user add index(phone);
alter table user drop emailVerifyCode;
alter table user drop emailVerifyTime;
alter table recommendation add hasRead char(1) default null;

alter table sms add userId int default null;
alter table email_task add userId int default null;


alter table user_wechat modify userId int default null;

#检查
select phone,count(*) cnt from user where (phone is not null and phone !='') and (active is null or active!='D') group by phone having cnt>1;

alter table user_organization_rel drop trial;
alter table user_organization_rel drop serviceEndDate;
alter table user_organization_rel drop trailCount;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`user_preference` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `type` INT NULL COMMENT '1. round 2.location',
  `preference` VARCHAR(100) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_user_round_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_user_round_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `tsb_v2`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

#以下升级时执行
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#非认证投资人
update user set verifiedInvestor='N' where id in (
460,943,155,425,951,981,897,356,949,711,489,665,
772,1061,817,884,1054,881,1065,1066,1057,1055,
1053,993,997,996,989,992,986,977,778,990,978,967
,966,962,887,886,831,798,916,918,912,702,899,895,862
,900,815,686,626,535,438,825,824,950,948,844,784,638,652
,632,618,120,139,240,261,286,1069
);

update user set verifiedInvestor='Y' where verifiedInvestor is null or verifiedInvestor!='N';

#FA
update user set userIdentify=61020 where id in (
460,943,155,425,951,981,897,356,949
);

#创业者
update user set userIdentify=61030 where id in (
711,489
);

#其他
update user set userIdentify=61040 where id in (
665,772,1061,817,884,1054,881
);

update user set userIdentify=61010 where userIdentify is null or userIdentify<61010;
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#以上升级时执行


CREATE TABLE IF NOT EXISTS `tsb_v2`.`user_start_trial` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_user_start_trial_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_user_start_trial_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `tsb_v2`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table user_start_trial add orgId int not null;

alter table user_deal_panel add orgId int default null;

