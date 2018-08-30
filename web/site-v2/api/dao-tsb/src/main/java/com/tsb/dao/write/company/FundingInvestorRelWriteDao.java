package com.tsb.dao.write.company;

import com.tsb.model.company.FundingInvestorRel;

public interface FundingInvestorRelWriteDao {
	void insert(FundingInvestorRel fundingInvestorRel);
	void update(FundingInvestorRel fundingInvestorRel);
	void delete(Integer id);
}
