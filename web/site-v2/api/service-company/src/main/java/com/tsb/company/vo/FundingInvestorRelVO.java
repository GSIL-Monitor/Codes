package com.tsb.company.vo;

import com.tsb.model.company.FundingInvestorRel;
import com.tsb.model.company.Investor;

public class FundingInvestorRelVO {
	private FundingInvestorRel fir;
	private Investor investor;
	public FundingInvestorRel getFir() {
		return fir;
	}
	public void setFir(FundingInvestorRel fir) {
		this.fir = fir;
	}
	public Investor getInvestor() {
		return investor;
	}
	public void setInvestor(Investor investor) {
		this.investor = investor;
	}
	
}
