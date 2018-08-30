#基金维护功能有关

alter table investor add online char(1) not null default 'N';
alter table investor add index (`online`);
alter table source_funding add newsUrl varchar(500) default null;
# alter table investor_alias drop gongchangCheckTime;
alter table company add statusDate datetime null default null;
alter table recommendation add hasNewFunding char(1) not null default 'N';
alter table organization add serviceStartDate datetime null;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`investor_alias_candidate` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `investorId` INT NOT NULL,
  `name` VARCHAR(200) NOT NULL,
  `type` INT NULL,
  `createTime` TIMESTAMP NULL,
  `candidate` CHAR(1) NULL DEFAULT 'N',
  `status` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_investor_company_investor1_idx` (`investorId` ASC),
  CONSTRAINT `fk_investor_company_investor10`
    FOREIGN KEY (`investorId`)
    REFERENCES `tsb_v2`.`investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `audit_investor_company` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `investorId` INT NOT NULL,
  `companyId` INT NULL,
  `xiniuInvestor` CHAR(1) NULL DEFAULT 'N',
  `itjuziInvestor` CHAR(1) NULL DEFAULT 'N',
  `kr36Investor` CHAR(1) NULL DEFAULT 'N',
  `gongshangInvestor` CHAR(1) NULL DEFAULT 'N',
  `createTime` TIMESTAMP NULL,
  `operator` INT NULL,
  `operateTime` TIMESTAMP NULL,
  `operateStatus` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_audit_investor_company_investor1_idx` (`investorId` ASC),
  INDEX `fk_audit_investor_company_company1_idx` (`companyId` ASC),
  CONSTRAINT `fk_audit_investor_company_investor1`
    FOREIGN KEY (`investorId`)
    REFERENCES `investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_audit_investor_company_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `audit_investor_company_source` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `auditInvestorCompanyId` INT NOT NULL,
  `source` INT NOT NULL,
  `sourceId` VARCHAR(32) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_audit_investor_company_source_audit_investor_company1_idx` (`auditInvestorCompanyId` ASC),
  CONSTRAINT `fk_audit_investor_company_source_audit_investor_company1`
    FOREIGN KEY (`auditInvestorCompanyId`)
    REFERENCES `audit_investor_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `stat_fund_declined_funding` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `statFundId` INT NOT NULL,
  `companyId` INT NOT NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_stat_fund_declined_funding_stat_fund1_idx` (`statFundId` ASC),
  CONSTRAINT `fk_stat_fund_declined_funding_stat_fund1`
    FOREIGN KEY (`statFundId`)
    REFERENCES `stat_fund` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


#
-- alter table location add id int default null;
-- alter table location add index (id);
-- update location set id=locationId;


alter table investor add establishDate datetime null;
alter table investor add locationId int null;

CREATE TABLE IF NOT EXISTS `investor_contact` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `investorId` INT NOT NULL,
  `locationId` INT NULL,
  `address` VARCHAR(500) NULL,
  `phone` VARCHAR(100) NULL,
  `email` VARCHAR(100) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `verify` CHAR(1) NULL,
  `active` VARCHAR(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_investor_contact_investor1_idx` (`investorId` ASC),
  CONSTRAINT `fk_investor_contact_investor1`
    FOREIGN KEY (`investorId`)
    REFERENCES `investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `investor_tag_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `investorId` INT NOT NULL,
  `tagId` INT NOT NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_investor_tag_rel_investor1_idx` (`investorId` ASC),
  INDEX `fk_investor_tag_rel_tag1_idx` (`tagId` ASC),
  CONSTRAINT `fk_investor_tag_rel_investor1`
    FOREIGN KEY (`investorId`)
    REFERENCES `investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_investor_tag_rel_tag1`
    FOREIGN KEY (`tagId`)
    REFERENCES `tag` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;