package com.tsb.company.vo;

import java.util.List;

import com.tsb.model.company.Funding;

public class FundingVO {
	private Funding funding;
	private List<FundingInvestorRelVO> firList;
	public Funding getFunding() {
		return funding;
	}
	public void setFunding(Funding funding) {
		this.funding = funding;
	}
	public List<FundingInvestorRelVO> getFirList() {
		return firList;
	}
	public void setFirList(List<FundingInvestorRelVO> firList) {
		this.firList = firList;
	}
}
