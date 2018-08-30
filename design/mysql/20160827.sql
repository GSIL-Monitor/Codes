CREATE TABLE IF NOT EXISTS `tsb_v2`.`audit_source_company` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `source_company_id` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  `taker` INT NULL,
  `takeTime` TIMESTAMP NULL,
  `processStatus` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_audit_source_company_source_company1_idx` (`source_company_id` ASC),
  INDEX `idx_audit_source_company_1` (`processStatus` ASC, `taker` ASC, `createTime` ASC),
  CONSTRAINT `fk_audit_source_company_source_company1`
    FOREIGN KEY (`source_company_id`)
    REFERENCES `tsb_v2`.`source_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


alter table source_company add auditor int null,
add auditTime TIMESTAMP null,
add auditMemo text null;

alter table source_company_member_rel modify verify char(1) default null;

alter table company add shouldIndex int default null;

alter table company_fa add bp_name varchar(500) default null after companyId;
alter table company_fa add bp_link varchar(50) default null after bp_name;
alter table company_fa drop column bp;

