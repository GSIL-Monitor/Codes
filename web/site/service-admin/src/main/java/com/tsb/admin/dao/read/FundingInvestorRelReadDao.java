package com.tsb.admin.dao.read;

import java.util.List;

import com.tsb.model.FundingInvestorRel;

public interface FundingInvestorRelReadDao {
	List<FundingInvestorRel> get(Integer fundingId);
	
}
