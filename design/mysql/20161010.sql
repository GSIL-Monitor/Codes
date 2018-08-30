alter table collection add processStatus int default null;
update collection set processStatus=1;

alter table funding add investorsRaw text default null;
alter table funding add investors text default null;
alter table funding add newsId varchar(100) default null;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`audit_reaggregate_company` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type` INT NULL COMMENT '1.merge -1.split',
  `beforeProcess` TEXT NULL,
  `afterProcess` TEXT NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `processStatus` INT NULL COMMENT '-1. deny 0.init 1.should 2.done',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`comps` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `processStatus` INT NULL DEFAULT 0 COMMENT '0. edit 1.should 2.done',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`comps_company_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `compsId` INT NOT NULL,
  `companyId` INT NOT NULL,
  `sort` INT NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_comps_company_rel_comps1_idx` (`compsId` ASC),
  INDEX `fk_comps_company_rel_company1_idx` (`companyId` ASC),
  CONSTRAINT `fk_comps_company_rel_comps1`
    FOREIGN KEY (`compsId`)
    REFERENCES `tsb_v2`.`comps` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comps_company_rel_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`audit_reaggregate_investor` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type` INT NULL COMMENT '1.merge -1.split',
  `beforeProcess` TEXT NULL,
  `afterProcess` TEXT NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `processStatus` INT NULL COMMENT '-1. deny 0.init 1.should 2.done',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


alter table company_fa add eventName varchar(200) default null;
alter table company_fa add eventResult text default null;
alter table company_fa add endDate datetime default null;


alter table collection add isNew char(1) default null;


