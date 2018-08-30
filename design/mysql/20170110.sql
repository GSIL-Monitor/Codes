delete from sourcedeal_file;
delete from sourcedeal_forward;
delete from sourcedeal_process;
delete from sourcedeal;

drop table sourcedeal_file;
drop table sourcedeal_forward;
drop table sourcedeal_process;
drop table sourcedeal;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`sourcedeal` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(500) NOT NULL,
  `content` TEXT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyUser` INT NULL,
  `assignee` INT NULL,
  `sponsor` INT NULL,
  `origin` VARCHAR(100) NULL,
  `followStatus` INT NULL,
  `note` TEXT NULL,
  `orgId` INT NULL,
  `titleMd5` VARCHAR(32) NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_sourcedeal1` (`orgId` ASC, `assignee` ASC, `followStatus` ASC),
  INDEX `idx_sourcedeal2` (`orgId` ASC, `sponsor` ASC, `followStatus` ASC),
  INDEX `idx_sourcedeal3` (`orgId` ASC, `titleMd5` ASC))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`sourcedeal_file` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sourcedealId` INT NOT NULL,
  `filename` VARCHAR(500) NULL,
  `fileId` VARCHAR(50) NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_lead_file_lead1_idx` (`sourcedealId` ASC),
  CONSTRAINT `fk_lead_file_lead1`
    FOREIGN KEY (`sourcedealId`)
    REFERENCES `tsb_v2`.`sourcedeal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`sourcedeal_forward` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sourcedealId` INT NOT NULL,
  `fromUserId` INT NULL,
  `toUserId` INT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_lead_forward_lead1_idx` (`sourcedealId` ASC),
  CONSTRAINT `fk_lead_forward_lead1`
    FOREIGN KEY (`sourcedealId`)
    REFERENCES `tsb_v2`.`sourcedeal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS `tsb_v2`.`sourcedeal_process` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sourcedealId` INT NOT NULL,
  `status` INT NOT NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_sourcedeal_process_sourcedeal1_idx` (`sourcedealId` ASC),
  INDEX `idx_sp_status` (`status` ASC),
  CONSTRAINT `fk_sourcedeal_process_sourcedeal1`
    FOREIGN KEY (`sourcedealId`)
    REFERENCES `tsb_v2`.`sourcedeal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;