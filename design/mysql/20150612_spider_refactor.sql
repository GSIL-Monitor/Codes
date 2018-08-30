1.
#简化source_company与company相关表的关系
#只保留company, member, investor, investor_member与其source的关系

#source_artifact
alter table source_artifact drop foreign key fk_source_artifact_artifact1;
#alter table source_artifact drop column artifactId;
#把source_artifact中的domain补上后drop

#source_document
alter table source_document drop foreign key fk_source_document_document1;
alter table source_document drop column documentId;
#source_job
alter table source_job drop foreign key fk_source_job_job1;
alter table source_job drop column jobId;
#source_footprint
alter table source_footprint drop foreign key fk_source_footprint_footprint1;
alter table source_footprint drop column footprintId;
#source_funding
alter table source_funding drop foreign key fk_source_funding_funding1;
alter table source_funding drop column fundingId;
#source_company_member_rel
alter table source_company_member_rel drop foreign key fk_source_company_member_rel_company_member_rel1;
alter table source_company_member_rel drop column companyMemberRelId;
#source_funding_investor_rel
alter table source_funding_investor_rel drop foreign key fk_source_funding_investor_rel_funding_investor_rel1;
alter table source_funding_investor_rel drop column fundingInvestorRelId;

2.
#source_artifact增加domain, active
#domain(website domain, android pkgname, itunes trackId)
#active 'Y'保留 'N'删除
alter table source_artifact 
add column domain varchar(200) default null after link,
add column active char(1) default null after verify;
#把source_artifact中的domain补上


alter table source_artifact
add column extended char(1) default null;

3. *
#domain表改为beian(mongodb)
#去掉companyId
#drop table domain;

#******* 把source_domain中的数据导入beian(mongodb) ********
#source_domain删除(有数据)
#drop table source_domain;


4.
#source_company 增加 active 'Y'保留 'N'删除
#source_company增加processStauts, 0未处理 1扩展完成 2聚合完成
#删除 source_company_aggregate_status
alter table source_company 
add column active char(1) default null after verify,
add column processStatus int default 0 after active;
update source_company set processStatus=2;

drop table source_company_aggregate_status;

5.
#删除 source_artifact_market (无数据)
#删除 source_artifact_website (无数据)
drop table source_artifact_market;
drop table source_artifact_website;

6. *
#删除artifact_market(有数据, trends使用)(android_market代替)
#删除artifact_pic(有数据)
#删除，不用迁移
先不删除，等重构完成再删除

7.
#删除company_report(无数据)
drop table company_report;
#删除homepage(有数据，似乎无用)
先不删除
#删除investor_tag_rel(无数据)
drop table investor_tag_rel;

8. *
#迁移后删除 gongshang_base， gonshang
#迁移后删除 source_gongshang_base (有数据，同gongshang_base?)
迁移到mongo
先不删除，等重构完成再删除

9. *
#删除 homepage, 功能同 webiste(mongodb)

10. 
#source_investor, source_member 增加processStauts, 0未处理 1扩展完成 2聚合完成
alter table source_investor add column processStatus int default 0;
update source_investor set processStatus=2;
alter table source_member add column processStatus int default 0;
update source_member set processStatus=2;
alter table source_funding add column processStatus int default 0;
update source_funding set processStatus=2;


11.


CREATE TABLE IF NOT EXISTS `source_company_name` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sourceCompanyId` INT NOT NULL,
  `type` INT NULL,
  `name` VARCHAR(1000) NOT NULL,
  `verify` CHAR(1) NULL,
  `chinese` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `extended` char(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_source_company_fullname_source_company1_idx` (`sourceCompanyId` ASC),
  CONSTRAINT `fk_source_company_fullname_source_company1`
    FOREIGN KEY (`sourceCompanyId`)
    REFERENCES `source_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `source_mainbeianhao` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sourceCompanyId` INT NOT NULL,
  `mainBeianhao` VARCHAR(100) NULL,
  `verify` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_source_mainbeianhao_source_company1_idx` (`sourceCompanyId` ASC),
  CONSTRAINT `fk_source_mainbeianhao_source_company1`
    FOREIGN KEY (`sourceCompanyId`)
    REFERENCES `source_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
