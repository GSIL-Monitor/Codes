package com.tsb.dao.write;

import com.tsb.model.FundingInvestorRel;

public interface FundingInvestorRelWriteDao {
	Integer insert(FundingInvestorRel fir);
	void update(FundingInvestorRel fir);
}
