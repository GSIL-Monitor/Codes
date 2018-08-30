CREATE TABLE IF NOT EXISTS `tsb_v2`.`quarterly_report` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `dealId` INT NOT NULL,
  `title` VARCHAR(500) NULL,
  `createUser` INT NULL,
  `createTime` TIMESTAMP NULL,
  `modifyUser` INT NULL,
  `modifyTime` TIMESTAMP NULL,
  `active` CHAR(1) NULL,
  `processStatus` INT NOT NULL DEFAULT 0 COMMENT '0. generating 1. ready -1. fail',
  `fundId` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_quarterly_report_deal1_idx` (`dealId` ASC),
  INDEX `fk_quarterly_report_fund1_idx` (`fundId` ASC),
  CONSTRAINT `fk_quarterly_report_deal1`
    FOREIGN KEY (`dealId`)
    REFERENCES `tsb_v2`.`deal` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_quarterly_report_fund1`
    FOREIGN KEY (`fundId`)
    REFERENCES `tsb_v2`.`fund` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
