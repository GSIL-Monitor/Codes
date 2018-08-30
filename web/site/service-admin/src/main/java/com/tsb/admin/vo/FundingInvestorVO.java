package com.tsb.admin.vo;

import java.util.List;

import com.tsb.model.FundingInvestorRel;
import com.tsb.model.Investor;

public class FundingInvestorVO {
	private FundingInvestorRel fundingInvestorRel;
	private Investor investor;
	public FundingInvestorRel getFundingInvestorRel() {
		return fundingInvestorRel;
	}
	public void setFundingInvestorRel(FundingInvestorRel fundingInvestorRel) {
		this.fundingInvestorRel = fundingInvestorRel;
	}
	public Investor getInvestor() {
		return investor;
	}
	public void setInvestor(Investor investor) {
		this.investor = investor;
	}
	
}
