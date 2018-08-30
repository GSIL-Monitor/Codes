package com.tsb.admin.vo;

import java.util.List;

import com.tsb.model.Funding;

public class FundingVO {
	private Funding funding;
	private List<FundingInvestorVO> fundingInvestorList;
	public Funding getFunding() {
		return funding;
	}
	public void setFunding(Funding funding) {
		this.funding = funding;
	}
	public List<FundingInvestorVO> getFundingInvestorList() {
		return fundingInvestorList;
	}
	public void setFundingInvestorList(List<FundingInvestorVO> fundingInvestorList) {
		this.fundingInvestorList = fundingInvestorList;
	}
	
	
}
