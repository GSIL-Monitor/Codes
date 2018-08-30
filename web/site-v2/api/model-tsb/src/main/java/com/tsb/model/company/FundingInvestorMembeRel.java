package com.tsb.model.company;

public class FundingInvestorMembeRel {

	private Integer id;
	private Integer investorMemberId;
	private Integer fundingInvestorRelId;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getInvestorMemberId() {
		return investorMemberId;
	}

	public void setInvestorMemberId(Integer investorMemberId) {
		this.investorMemberId = investorMemberId;
	}

	public Integer getFundingInvestorRelId() {
		return fundingInvestorRelId;
	}

	public void setFundingInvestorRelId(Integer fundingInvestorRelId) {
		this.fundingInvestorRelId = fundingInvestorRelId;
	}

}
