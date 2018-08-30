package com.tsb.company.service;

import java.util.List;

import com.tsb.model.company.Funding;
import com.tsb.model.company.FundingInvestorRel;

@SuppressWarnings("rawtypes")
public interface FundingService {
	List get(int companyId);

	void addFundings(List fundings);

	void deleteFundings(List<Integer> ids,Integer userId);

	void updateFunding(Funding funding);

	void addFunding(Funding funding);

	void addFirs(List<FundingInvestorRel> firList,Integer userId);
	
	void deleteFirs(List<FundingInvestorRel> firList,Integer userId);
	
	void addFundingAndFirList(Funding funding,List<FundingInvestorRel> firList,Integer userId);
}
