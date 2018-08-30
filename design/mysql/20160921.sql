alter table company_fa modify companyId int default null;
alter table company_fa add field varchar(100) default null;
alter table company_fa add investmentHistory varchar(500) default null;
alter table company_fa add investorHistory varchar(500) default null;
alter table company_fa add modelDesc text default null after operationDesc;
alter table company_fa add planDesc text default null after modelDesc;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`company_fa_candidate` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyFaId` INT NOT NULL,
  `companyId` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_company_fa_candidate_company_fa1_idx` (`companyFaId` ASC),
  INDEX `fk_company_fa_candidate_company1_idx` (`companyId` ASC),
  CONSTRAINT `fk_company_fa_candidate_company_fa1`
    FOREIGN KEY (`companyFaId`)
    REFERENCES `tsb_v2`.`company_fa` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_company_fa_candidate_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`company_fa_news_candidate` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyFaId` INT NOT NULL,
  `newsId` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_company_fa_news_candidate_company_fa1_idx` (`companyFaId` ASC),
  CONSTRAINT `fk_company_fa_news_candidate_company_fa1`
    FOREIGN KEY (`companyFaId`)
    REFERENCES `tsb_v2`.`company_fa` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

#
alter table source_company add diffResult int default null;
alter table source_artifact add diffResult int default null;
alter table source_artifact add diffPosition int default null;
alter table source_company_name add diffResult int default null;
alter table source_company_name add diffPosition int default null;
alter table source_company_member_rel add diffResult int default null;
alter table source_company_member_rel add diffPosition int default null;
alter table source_funding add diffResult int default null;
alter table source_funding add diffPosition int default null;

alter table company_fa add newsId varchar(100) default null after companyId;
alter table company_fa add sourceId varchar(100) default null after source;
alter table company_fa add founder varchar(100) default null after planDesc;
alter table company_fa add founderDesc text default null after founder;

alter table company_fa add processStatus int not null default 0;


#
insert fa_advisor(id,source,name,wechat,createTime,active) 
values(18,13800,'铅笔道','Pencil-news',now(),'Y'); 

#
alter table company_fa add name varchar(200) default null after id;

alter table news_domain add important char(1) default null;

update news_domain set important='Y' where id in (4,5,6,7,8,49);

alter table collection add ruleMd5 varchar(32) default null after rule;
alter table collection add index idx_collection_rulemd5 (ruleMd5);


delete from company_fa_candidate where companyFaId in (select id from company_fa where source=13800);
delete from company_fa_news_candidate where companyFaId in (select id from company_fa where source=13800);
delete from company_fa_advisor_rel where companyFaId in (select id from company_fa where source=13800);
delete from company_fa where source=13800;

alter table company_fa modify `processStatus` int(11) default null;

#发布前调整
update company_fa set modelDesc=advantageDesc where source!=13800;
update company_fa set advantageDesc=productDesc where source!=13800;
update company_fa set productDesc=null where source!=13800;
update welcome set content='假期，与你一起出发。' where id=1;
