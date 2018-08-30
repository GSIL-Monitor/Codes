package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.FundingInvestorRel;

public interface FundingInvestorRelReadDao {

	List<FundingInvestorRel> get(int fundingId);
}
