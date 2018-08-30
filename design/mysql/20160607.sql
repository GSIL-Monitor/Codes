alter table deal 
add moneyRemainMonth int default null,
add recordDate datetime default null,
add exitPlan text default null;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`fund` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `organizationId` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_fund_organization1_idx` (`organizationId` ASC),
  CONSTRAINT `fk_fund_organization1`
    FOREIGN KEY (`organizationId`)
    REFERENCES `tsb_v2`.`organization` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_investment` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `fundId` INT NOT NULL,
  `date` DATETIME NULL,
  `round` INT NULL,
  `totalInvestment` VARCHAR(45) NULL,
  `fundInvestment` VARCHAR(45) NULL,
  `currency` INT NULL,
  `shareRatio` FLOAT NULL,
  `postMoney` VARCHAR(45) NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_investment_fund1_idx` (`fundId` ASC),
  INDEX `fk_deal_investment_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_investment_fund1`
    FOREIGN KEY (`fundId`)
    REFERENCES `tsb_v2`.`fund` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_deal_investment_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_investment_process` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `orgName` VARCHAR(45) NULL,
  `TSDate` DATETIME NULL,
  `SPADate` DATETIME NULL,
  `round` INT NULL,
  `planInvestment` VARCHAR(45) NULL,
  `orgInvestment` VARCHAR(45) NULL,
  `currency` INT NULL,
  `shareRatio` FLOAT NULL,
  `postMoney` VARCHAR(45) NULL,
  `status` INT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_investment_process_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_investment_process_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_cap_table` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealInvestmentId` INT NOT NULL,
  `shareholder` VARCHAR(200) NULL,
  `registerAmount` VARCHAR(45) NULL,
  `shareRatio` FLOAT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  INDEX `fk_deal_cap_table_deal_investment1_idx` (`dealInvestmentId` ASC),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_deal_cap_table_deal_investment1`
    FOREIGN KEY (`dealInvestmentId`)
    REFERENCES `tsb_v2`.`deal_investment` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_finance` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `startDate` DATETIME NULL,
  `endDate` DATETIME NULL,
  `revenue` VARCHAR(45) NULL,
  `revenueRatio` FLOAT NULL,
  `expense` VARCHAR(45) NULL,
  `expenseRatio` FLOAT NULL,
  `profit` VARCHAR(45) NULL,
  `profitRatio` FLOAT NULL,
  `surplus` VARCHAR(45) NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_finance_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_finance_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_finance_expand` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_finance_expand_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_finance_expand_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_finance_expand_value` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealFinanceExpandId` INT NOT NULL,
  `dealFinanceId` INT NOT NULL,
  `content` TEXT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_finance_expand_value_deal_finance_expand1_idx` (`dealFinanceExpandId` ASC),
  INDEX `fk_deal_finance_expand_value_deal_finance1_idx` (`dealFinanceId` ASC),
  CONSTRAINT `fk_deal_finance_expand_value_deal_finance_expand1`
    FOREIGN KEY (`dealFinanceExpandId`)
    REFERENCES `tsb_v2`.`deal_finance_expand` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_deal_finance_expand_value_deal_finance1`
    FOREIGN KEY (`dealFinanceId`)
    REFERENCES `tsb_v2`.`deal_finance` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_artifact_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `artifactId` INT NOT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_artifact_rel_deal1_idx` (`dealId` ASC),
  INDEX `fk_deal_artifact_rel_artifact1_idx` (`artifactId` ASC),
  CONSTRAINT `fk_deal_artifact_rel_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_deal_artifact_rel_artifact1`
    FOREIGN KEY (`artifactId`)
    REFERENCES `tsb_v2`.`artifact` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_business` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `startDate` DATETIME NULL,
  `endDate` DATETIME NULL,
  `progress` TEXT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_business_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_business_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_business_expand` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `name` VARCHAR(200) NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL COMMENT ' ',
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_business_expand_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_business_expand_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_business_expand_value` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealBusinessExpandId` INT NOT NULL,
  `dealBusinessId` INT NOT NULL,
  `content` TEXT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_business_expand_value_deal_business1_idx` (`dealBusinessId` ASC),
  INDEX `fk_deal_business_expand_value_deal_business_expand1_idx` (`dealBusinessExpandId` ASC),
  CONSTRAINT `fk_deal_business_expand_value_deal_business1`
    FOREIGN KEY (`dealBusinessId`)
    REFERENCES `tsb_v2`.`deal_business` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_deal_business_expand_value_deal_business_expand1`
    FOREIGN KEY (`dealBusinessExpandId`)
    REFERENCES `tsb_v2`.`deal_business_expand` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_comps` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `companyId` INT NULL,
  `sort` INT NULL,
  `status` INT NULL,
  `type` INT NULL,
  `establishDate` DATETIME NULL,
  `locationId` INT NULL,
  `round` INT NULL,
  `investment` VARCHAR(45) NULL,
  `investor` VARCHAR(200) NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_comps_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_comps_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`deal_file` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `fileId` VARCHAR(500) NULL,
  `type` INT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_deal_file_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_deal_file_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `tsb_v2`.`alarm` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NULL,
  `alarmTime` TIMESTAMP NULL,
  `content` TEXT NULL,
  `active` CHAR(1) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_alarm_deal1_idx` (`dealId` ASC),
  CONSTRAINT `fk_alarm_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


ALTER TABLE `tsb_v2`.`deal_finance` 
CHANGE COLUMN `revenueRatio` `revenueRatio` VARCHAR(45) NULL DEFAULT NULL ,
CHANGE COLUMN `expenseRatio` `expenseRatio` VARCHAR(45) NULL DEFAULT NULL ,
CHANGE COLUMN `profitRatio` `profitRatio` VARCHAR(45) NULL DEFAULT NULL ;

