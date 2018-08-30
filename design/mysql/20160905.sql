alter table source_company add recommendCompanyIds varchar(200) default null;

alter table company add privatization CHAR(1) default null;

alter table company add website varchar(300) default null after fullName;


#
CREATE TABLE IF NOT EXISTS `tsb_v2`.`company_fa` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyId` INT NOT NULL,
  `bp` VARCHAR(100) NULL,
  `source` INT NOT NULL,
  `publishDate` DATETIME NOT NULL,
  `round` INT NULL,
  `currency` INT NULL,
  `investmentMin` INT NULL,
  `investmentMax` INT NULL,
  `shareRatioMin` FLOAT NULL,
  `shareRationMax` FLOAT NULL,
  `description` TEXT NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `active` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_company_fa_company1_idx` (`companyId` ASC),
  CONSTRAINT `fk_company_fa_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`fa_advisor` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `source` INT NULL,
  `name` VARCHAR(100) NULL,
  `phone` VARCHAR(100) NULL,
  `wechat` VARCHAR(100) NULL,
  `email` VARCHAR(100) NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `active` CHAR(1) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`company_fa_advisor_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `companyFaId` INT NOT NULL,
  `faAdvisorId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `active` CHAR(1) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_comany_fa_advisor_rel_company_fa1_idx` (`companyFaId` ASC),
  INDEX `fk_comany_fa_advisor_rel_fa_advisor1_idx` (`faAdvisorId` ASC),
  CONSTRAINT `fk_comany_fa_advisor_rel_company_fa1`
    FOREIGN KEY (`companyFaId`)
    REFERENCES `tsb_v2`.`company_fa` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comany_fa_advisor_rel_fa_advisor1`
    FOREIGN KEY (`faAdvisorId`)
    REFERENCES `tsb_v2`.`fa_advisor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table company_fa add advantageDesc text default null after description;
alter table company_fa add marketDesc text default null after advantageDesc;
alter table company_fa add productDesc text default null after marketDesc;
alter table company_fa add operationDesc text default null after productDesc;
alter table company_fa drop description;

alter table company_fa change shareRationMax shareRatioMax float default null;


CREATE TABLE `tsb_v2`.`special_tag` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `sort` float DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_special_tag_tag1_idx` (`id`),
  CONSTRAINT `fk_special_tag_tag1` FOREIGN KEY (`id`) REFERENCES `tag` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`welcome` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `content` TEXT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`hot_search` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

alter table artifact add releaseDate datetime default null;

alter table artifact modify rank bigint default 0;

