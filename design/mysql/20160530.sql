alter table investor add display char(1) default null after type;

CREATE TABLE IF NOT EXISTS `investor_company_rel` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `investorId` INT NOT NULL,
  `companyId` INT NOT NULL,
  `type` INT NOT NULL,
  `sort` FLOAT NOT NULL,
  `createTime` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_investor_company_rel_investor1_idx` (`investorId` ASC),
  INDEX `fk_investor_company_rel_company1_idx` (`companyId` ASC),
  CONSTRAINT `fk_investor_company_rel_investor1`
    FOREIGN KEY (`investorId`)
    REFERENCES `investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_investor_company_rel_company1`
    FOREIGN KEY (`companyId`)
    REFERENCES `company` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `investor_chart` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `investorId` INT NOT NULL,
  `type` INT NOT NULL,
  `file` VARCHAR(100) NOT NULL,
  `createTime` TIMESTAMP NOT NULL,
  `modifyTime` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_investor_chart_investor1_idx` (`investorId` ASC),
  CONSTRAINT `fk_investor_chart_investor1`
    FOREIGN KEY (`investorId`)
    REFERENCES `investor` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

alter table deal add createUser int default null after shareRatio;