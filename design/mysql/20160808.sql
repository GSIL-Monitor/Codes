alter table job add source int default null after offline;
alter table job add index (modifyTime,offline);

alter table source_artifact add expanded char(1) default null;
alter table source_company_name add expanded char(1) default null;
alter table source_mainbeianhao add expanded char(1) default null;


#2016/8/9 检查
update job set source=13050 where source is null;



#track
CREATE TABLE IF NOT EXISTS `track_topic` (
  `id` INT NOT NULL,
  `type` INT NULL,
  `name` VARCHAR(100) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `subscription` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `topicId` INT NOT NULL,
  `companyId` INT NULL,
  `tagId` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `verify` VARCHAR(1) NULL,
  `active` VARCHAR(1) NULL DEFAULT 'Y',
  PRIMARY KEY (`id`),
  INDEX `fk_subscription_user1_idx` (`userId` ASC),
  INDEX `fk_subscription_company1_idx` (`companyId` ASC),
  INDEX `fk_subscription_topic1_idx` (`topicId` ASC),
  INDEX `fk_subscription_tag1_idx` (`tagId` ASC),
  CONSTRAINT `fk_subscription_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_subscription_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_subscription_topic1`
    FOREIGN KEY (`topicId`)
    REFERENCES `track_topic` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_subscription_tag1`
    FOREIGN KEY (`tagId`)
    REFERENCES `tag` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


#2016/8/10
CREATE TABLE IF NOT EXISTS `tsb_v2`.`dictionary` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `typeValue` INT NULL,
  `typeName` VARCHAR(45) NULL,
  `subTypeValue` INT NULL,
  `subTypeName` VARCHAR(45) NULL,
  `value` INT NULL,
  `name` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_dict1` (`typeValue` ASC),
  INDEX `idx_dict2` (`subTypeValue` ASC),
  UNIQUE INDEX `idx_dict3` (`value` ASC))
ENGINE = InnoDB;

insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1301, 'FA', 13100, '以太');
insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1301, 'FA', 13101, '华兴Alpha');
insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1301, 'FA', 13102, '小饭桌');
insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1301, 'FA', 13103, '36Kr');
insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1301, 'FA', 13104, '方创');
insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1301, 'FA', 13105, 'IPRdaily');
insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1302, '孵化器', 13300, '微软加速器');
insert dictionary(typeValue,typeName,subTypeValue,subTypeName,value,name)
values(13,'来源', 1302, '孵化器', 13301, '氪空间');


#deal 有关
alter table deal
add name varchar(200) default null,
add fullName varchar(200) default null,
add description text default null,
add locationId int default null,
add address varchar(200) default null,
add phone varchar(200) default null,
add establishDate datetime default null,
add logo varchar(200) default null,
add privatization char(1) default null,
add verify char(1) default null,
add verifyUser int default null,
add verifyTime TIMESTAMP NULL;


alter table deal_artifact_rel add follow char(1) default null;
#update deal_artifact_rel set follow='Y' where active='Y';
#update deal_artifact_rel set active=null where follow='Y';

alter table deal_funding add investor varchar(1000) default null;

CREATE TABLE IF NOT EXISTS `deal_tag` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `type` INT NULL,
  `weight` FLOAT NULL,
  `novelty` FLOAT NULL,
  `hot` CHAR(1) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `deal_tag_un_name` (`name` ASC))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `deal_tag_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `dealTagId` INT NOT NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_tag_rel_deal1_idx` (`dealId` ASC),
  INDEX `fk_deal_tag_rel_deal_tag1_idx` (`dealTagId` ASC),
  CONSTRAINT `fk_deal_tag_rel_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_deal_tag_rel_deal_tag1`
    FOREIGN KEY (`dealTagId`)
    REFERENCES `deal_tag` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `deal_artifact_new` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `name` VARCHAR(1000) NULL,
  `description` TEXT NULL,
  `link` VARCHAR(500) NULL,
  `type` INT NULL,
  `procceed` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_artifact_new_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_artifact_new_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `deal_member` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `name` VARCHAR(100) NULL,
  `education` TEXT NULL,
  `workEmphasis` TEXT NULL,
  `work` TEXT NULL,
  `description` TEXT NULL,
  `photo` VARCHAR(200) NULL,
  `email` VARCHAR(200) NULL,
  `phone` VARCHAR(20) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_member_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_member_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table deal add modifyUser int default null after createTime;
alter table deal_member add position varchar(100) default null after name;

alter table deal_funding add precise char(1) default null after currency;


#2016/08/19
CREATE TABLE IF NOT EXISTS `crawler_v2`.`spider_stats` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `statsDate` DATETIME NOT NULL,
  `categoryId` INT NULL,
  `categoryName` VARCHAR(100) NULL,
  `source` INT NULL,
  `sourceName` VARCHAR(100) NULL,
  `type` INT NULL,
  `typeName` VARCHAR(100) NULL,
  `createNum` INT NULL,
  `updateNum` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

alter table deal_artifact_new change procceed `proceed` CHAR(1) NULL;
alter table deal_artifact_new add verify char(1) default null;
alter table deal_artifact_new add sourceArtifactId int default null;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`news_domain` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `domain` VARCHAR(200) NOT NULL,
  `name` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

insert news_domain(domain,name) values('sina.com.cn', '新浪');
insert news_domain(domain,name) values('qq.com', '腾讯');
insert news_domain(domain,name) values('investide.cn', '投资潮');