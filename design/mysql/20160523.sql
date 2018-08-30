alter table organization add logo varchar(200) default null;


CREATE TABLE IF NOT EXISTS `deal_flow` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `status` INT NULL,
  `declineStatus` INT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_log_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_log_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `deal_funding` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `fundingDate` DATETIME NULL,
  `round` INT NULL,
  `roundDesc` VARCHAR(100) NULL,
  `preMoney` BIGINT NULL,
  `postMoney` BIGINT NULL,
  `investment` BIGINT NULL,
  `shareRatio` FLOAT NULL,
  `currency` INT NULL,
  `totalInvestment` BIGINT NULL,
  `totalShareRatio` FLOAT NULL,
  `totalCurrency` INT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_funding_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_funding_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `deal_note_message` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealNoteId` INT NOT NULL,
  `userId` INT NOT NULL,
  `visitTime` TIMESTAMP NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_note_message_deal_note1_idx` (`dealNoteId` ASC),
  INDEX `fk_deal_note_message_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_deal_note_message_deal_note1`
    FOREIGN KEY (`dealNoteId`)
    REFERENCES `deal_note` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_deal_note_message_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

drop table deal_task;
alter table deal_note add fromDate datetime default null after note;
alter table deal_note add toDate datetime default null after fromDate;
alter table deal_note add iom char(1) default null after toDate;
alter table deal_note add active char(1) default null after iom;


DROP TABLE `hot_tag` ;

CREATE TABLE IF NOT EXISTS `hot_tag` (
  `id` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `sort` FLOAT NULL,
  `createTime` TIMESTAMP NULL,
  INDEX `fk_hot_tag_tag1_idx` (`id` ASC),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_hot_tag_tag1`
    FOREIGN KEY (`id`)
    REFERENCES `tag` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


alter table deal add round int default null after fundingType;
alter table deal add roundDesc varchar(45) default null after round;

#20150526
alter table deal add assignee int null;
alter table deal add sponsor int null;
alter table deal add CONSTRAINT `fk_deal_user1`
    FOREIGN KEY (`assignee`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
alter table deal add CONSTRAINT `fk_deal_user2`
    FOREIGN KEY (`sponsor`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

CREATE TABLE IF NOT EXISTS `iom_other_note` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `note` TEXT NULL,
  `fromDate` DATETIME NULL,
  `toDate` DATETIME NULL,
  `iom` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_iom_other_note_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_iom_other_note_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table company modify preMoney bigint(20) default null,
modify investment bigint(20) default null,
modify postMoney bigint(20) default null;

alter table funding modify preMoney bigint(20) default null,
modify postMoney bigint(20) default null,
modify investment bigint(20) default null;

alter table funding_investor_rel modify investment bigint(20) default null;

alter table source_company modify preMoney bigint(20) default null,
modify investment bigint(20) default null;

alter table source_funding modify preMoney bigint(20) default null,
modify postMoney bigint(20) default null,
modify investment bigint(20) default null;

alter table source_funding_investor_rel modify investment bigint(20) default null;

alter table deal modify preMoney bigint(20) default null,
modify investment bigint(20) default null,
modify postMoney bigint(20) default null;

alter table tag add hot char(1) default null after novelty;


