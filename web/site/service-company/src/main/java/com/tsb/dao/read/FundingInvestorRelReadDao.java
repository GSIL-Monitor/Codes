package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.FundingInvestorRel;


public interface FundingInvestorRelReadDao {
	List<FundingInvestorRel> get(int fundingId);
}
