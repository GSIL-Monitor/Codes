CREATE TABLE IF NOT EXISTS `tsb_v2`.`mylist` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NULL,
  `isPublic` CHAR(1) NULL,
  `active` CHAR(1) NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`user_mylist_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `mylistId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  `createUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  INDEX `fk_user_list_rel_user1_idx` (`userId` ASC),
  PRIMARY KEY (`id`),
  INDEX `fk_user_list_rel_list1_idx` (`mylistId` ASC),
  CONSTRAINT `fk_user_list_rel_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `tsb_v2`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_user_list_rel_list1`
    FOREIGN KEY (`mylistId`)
    REFERENCES `tsb_v2`.`mylist` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


#DROP TABLE IF EXISTS `tsb_v2`.`mylist_company_rel` ;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`mylist_company_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `mylistId` INT NOT NULL,
  `companyId` INT NOT NULL,
  `createTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_mylist_company_rel_mylist1_idx` (`mylistId` ASC),
  INDEX `fk_mylist_company_rel_company1_idx` (`companyId` ASC),
  CONSTRAINT `fk_mylist_company_rel_mylist1`
    FOREIGN KEY (`mylistId`)
    REFERENCES `tsb_v2`.`mylist` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_mylist_company_rel_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `tsb_v2`.`company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`registration` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NULL,
  `company` VARCHAR(500) NULL,
  `email` VARCHAR(100) NULL,
  `mobile` VARCHAR(20) NULL,
  `createTime` TIMESTAMP NULL,
  `proceed` CHAR(1) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


drop table user_wechat;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`user_wechat` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` INT NOT NULL,
  `openid` VARCHAR(100) NOT NULL,
  `nickname` VARCHAR(100) NULL,
  `sex` INT NULL,
  `province` VARCHAR(100) NULL,
  `city` VARCHAR(100) NULL,
  `country` VARCHAR(100) NULL,
  `headimgurl` VARCHAR(200) NULL,
  `createTime` TIMESTAMP NULL default null,
  `modifyTime` TIMESTAMP NULL default null,
  `accesstoken` VARCHAR(200) NULL,
  `expiresin` INT NULL,
  `refreshtoken` VARCHAR(200) NULL,
  `tokenTime` TIMESTAMP NULL default null,
  `loginIP` VARCHAR(50) NULL,
  `lastLoginTime` DATETIME NULL,
  INDEX `openid_idx` (`openid` ASC),
  PRIMARY KEY (`id`),
  INDEX `fk_user_wechat_user1_idx` (`userId` ASC),
  CONSTRAINT `fk_user_wechat_user1`
    FOREIGN KEY (`userId`)
    REFERENCES `tsb_v2`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table artifact add recommend char(1) default null;
