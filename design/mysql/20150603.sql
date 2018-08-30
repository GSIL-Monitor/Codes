alter table deal add portfolioStatus int default null;

alter table organization add active char(1) default null after logo;
alter table organization add verify char(1) default null after active;
alter table organization add createUser int default null after verify;
alter table organization add modifyUser int default null after createUser;


alter table demoday_company
add  `currentRound` INT NULL,
add  `currentRoundDesc` VARCHAR(50) NULL,
add  `preMoney` BIGINT NULL,
add  `investment` BIGINT NULL,
add  `postMoney` BIGINT NULL,
add  `shareRatio` FLOAT NULL,
add  `currency` INT(8) NULL;


update demoday_company d, company c set 
d.currentRound=c.currentRound,
d.currentRoundDesc=c.currentRoundDesc,
d.preMoney=c.preMoney,
d.investment=c.investment,
d.postMoney=c.postMoney,
d.shareRatio=c.shareRatio,
d.currency=c.currency
where d.companyId=c.id;