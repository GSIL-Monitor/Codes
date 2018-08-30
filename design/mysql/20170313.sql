# create table corporate
# create table corprate_alias

# add corporateId in company

# copy data from company to corporate
# copy data  from company_alias to corporate_alias

# remove some columns from company

# add corporateId in funding

# establish relation from funding to corporate

# remove companyId from funding
# remove companyId from funding_investor_rel


CREATE TABLE IF NOT EXISTS `corporate` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(45) NULL,
  `name` VARCHAR(1000) NULL,
  `fullName` VARCHAR(200) NULL,
  `website` VARCHAR(300) NULL,
  `brief` VARCHAR(200) NULL,
  `description` TEXT NULL,
  `round` INT(8) NULL,
  `roundDesc` VARCHAR(45) NULL,
  `corporateStatus` INT(8) NULL,
  `fundingType` INT(8) NULL,
  `currentRound` INT NULL,
  `currentRoundDesc` VARCHAR(45) NULL,
  `preMoney` BIGINT NULL,
  `investment` BIGINT NULL,
  `postMoney` BIGINT NULL,
  `shareRatio` FLOAT NULL,
  `currency` INT(8) NULL,
  `headCountMin` INT NULL,
  `headCountMax` INT NULL,
  `locationId` INT(8) NULL,
  `address` VARCHAR(200) NULL,
  `phone` VARCHAR(200) NULL,
  `establishDate` DATETIME NULL,
  `logo` VARCHAR(200) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  `statusDate` DATETIME NULL,
  `parentId` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `code` (`code` ASC))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `corporate_alias` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `corporateId` INT NOT NULL,
  `name` VARCHAR(200) NULL,
  `type` INT(8) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_corporate_alias_corporate1_idx` (`corporateId` ASC),
  CONSTRAINT `fk_corporate_alias_corporate1`
    FOREIGN KEY (`corporateId`)
    REFERENCES `corporate` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table company add `corporateId` INT default NULL;
alter table company add INDEX `fk_company_corporate1_idx` (`corporateId` ASC);
alter table company add CONSTRAINT `fk_company_corporate1`
FOREIGN KEY (`corporateId`)
REFERENCES `corporate` (`id`);

alter table funding add `corporateId` INT default NULL;
alter table funding add INDEX `fk_funding_corporate1_idx` (`corporateId` ASC);
alter table funding add CONSTRAINT `fk_funding_corporate1`
    FOREIGN KEY (`corporateId`)
    REFERENCES `corporate` (`id`);


#alter table corporate modify companyStatus corporateStatus INT(8) NULL;


alter table artifact add display char(1) default 'Y';
alter table funding modify companyId int null;
