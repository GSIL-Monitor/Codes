package com.tsb.admin.vo;

import com.tsb.model.source.SourceFundingInvestorRel;
import com.tsb.model.source.SourceInvestor;

public class SourceFundingInvestorVO {
	private SourceFundingInvestorRel sfiRel;
	private SourceInvestor sourceInvestor;
	public SourceFundingInvestorRel getSfiRel() {
		return sfiRel;
	}
	public void setSfiRel(SourceFundingInvestorRel sfiRel) {
		this.sfiRel = sfiRel;
	}
	public SourceInvestor getSourceInvestor() {
		return sourceInvestor;
	}
	public void setSourceInvestor(SourceInvestor sourceInvestor) {
		this.sourceInvestor = sourceInvestor;
	}
	
	
}
