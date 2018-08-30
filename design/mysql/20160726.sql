alter table job add column offline char(1) not null default 'N';


CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_company` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(45) NULL,
  `name` VARCHAR(1000) NULL,
  `fullName` VARCHAR(200) NULL,
  `description` TEXT NULL,
  `brief` VARCHAR(200) NULL,
  `round` INT(8) NULL,
  `roundDesc` VARCHAR(45) NULL,
  `companyStatus` INT(8) NULL,
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
  `type` INT NULL DEFAULT 41010,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  INDEX `code` (`code` ASC))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_company_alias` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyId` INT NOT NULL,
  `name` VARCHAR(200) NULL,
  `type` INT(8) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  `gongchangCheckTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_test_company_alias_test_company1_idx` (`companyId` ASC),
  CONSTRAINT `fk_test_company_alias_test_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`test_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_artifact` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyId` INT NOT NULL,
  `name` VARCHAR(1000) NULL,
  `description` TEXT NULL,
  `link` VARCHAR(200) NULL,
  `domain` VARCHAR(200) NULL,
  `alexa` CHAR(1) NULL,
  `type` INT(8) NOT NULL,
  `productId` INT NULL,
  `tags` VARCHAR(200) NULL,
  `others` TEXT NULL,
  `rank` INT NULL DEFAULT 0,
  `nameIndex` INT NULL,
  `nameIndexTime` TIMESTAMP NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  `recommend` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_product_company0`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`test_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_funding` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyId` INT NOT NULL,
  `preMoney` BIGINT NULL,
  `postMoney` BIGINT NULL,
  `investment` BIGINT NULL,
  `shareRatio` FLOAT NULL,
  `round` INT(8) NULL,
  `roundDesc` VARCHAR(45) NULL,
  `currency` INT(8) NULL,
  `precise` CHAR(1) NULL,
  `fundingDate` DATETIME NULL,
  `fundingType` INT(8) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_funding_company10`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`test_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_investor` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NULL,
  `website` VARCHAR(200) NULL,
  `domain` VARCHAR(100) NULL,
  `description` TEXT NULL,
  `logo` VARCHAR(100) NULL,
  `stage` TEXT NULL,
  `field` TEXT NULL,
  `type` INT NULL,
  `display` CHAR(1) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_funding_investor_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `fundingId` INT NOT NULL,
  `investorType` INT NOT NULL DEFAULT 38001,
  `investorId` INT NULL,
  `companyId` INT NULL,
  `currency` INT(8) NULL,
  `investment` BIGINT NULL,
  `precise` CHAR(1) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_funding_investor_rel_investor10`
    FOREIGN KEY (`investorId`)
    REFERENCES `tsb_v2`.`test_investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_funding_investor_rel_funding10`
    FOREIGN KEY (`fundingId`)
    REFERENCES `tsb_v2`.`test_funding` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_funding_investor_rel_company10`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`test_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_member` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(20) NULL,
  `education` TEXT NULL,
  `workEmphasis` TEXT NULL,
  `work` TEXT NULL,
  `description` TEXT NULL,
  `photo` VARCHAR(200) NULL,
  `email` VARCHAR(100) NULL,
  `phone` VARCHAR(20) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_company_member_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyId` INT NOT NULL,
  `memberId` INT NOT NULL,
  `position` VARCHAR(45) NULL,
  `joinDate` DATETIME NULL,
  `leaveDate` DATETIME NULL,
  `type` INT(8) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_company_member_rel_company10`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`test_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_company_member_rel_member10`
    FOREIGN KEY (`memberId`)
    REFERENCES `tsb_v2`.`test_member` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


alter table test_company
add column `productDesc` text,
add column `modelDesc` text,
add column `operationDesc` text,
add column `teamDesc` text,
add column `marketDesc` text,
add column `compititorDesc` text,
add column `advantageDesc` text,
add column `planDesc` text;


drop table test_funding_investor_rel;
drop table test_investor;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`test_funding_investor_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `fundingId` INT NOT NULL,
  `investorType` INT NOT NULL DEFAULT 38001,
  `investorId` INT NULL,
  `companyId` INT NULL,
  `currency` INT(8) NULL,
  `investment` BIGINT NULL,
  `precise` CHAR(1) NULL,
  `verify` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `confidence` FLOAT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_funding_investor_rel_investor10`
    FOREIGN KEY (`investorId`)
    REFERENCES `tsb_v2`.`investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_funding_investor_rel_funding10`
    FOREIGN KEY (`fundingId`)
    REFERENCES `tsb_v2`.`test_funding` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_funding_investor_rel_company10`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`test_company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


alter table test_member modify `name` VARCHAR(100) NULL;


alter table registration add position int default null after company;
