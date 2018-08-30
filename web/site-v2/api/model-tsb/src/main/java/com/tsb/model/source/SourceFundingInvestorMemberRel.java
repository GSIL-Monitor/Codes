package com.tsb.model.source;

public class SourceFundingInvestorMemberRel extends SourceBasicModel {

	private Integer id;
	private Integer sourceFundingInvestorReld;
	private Integer sourceInvestorMemberId;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getSourceFundingInvestorReld() {
		return sourceFundingInvestorReld;
	}

	public void setSourceFundingInvestorReld(Integer sourceFundingInvestorReld) {
		this.sourceFundingInvestorReld = sourceFundingInvestorReld;
	}

	public Integer getSourceInvestorMemberId() {
		return sourceInvestorMemberId;
	}

	public void setSourceInvestorMemberId(Integer sourceInvestorMemberId) {
		this.sourceInvestorMemberId = sourceInvestorMemberId;
	}

}
