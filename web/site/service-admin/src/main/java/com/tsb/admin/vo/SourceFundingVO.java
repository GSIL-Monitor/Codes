package com.tsb.admin.vo;

import java.util.List;

import com.tsb.model.source.SourceFunding;

public class SourceFundingVO {
	private SourceFunding sourceFunding;
	private List<SourceFundingInvestorVO> sfiVOList;
	public SourceFunding getSourceFunding() {
		return sourceFunding;
	}
	public void setSourceFunding(SourceFunding sourceFunding) {
		this.sourceFunding = sourceFunding;
	}
	public List<SourceFundingInvestorVO> getSfiVOList() {
		return sfiVOList;
	}
	public void setSfiVOList(List<SourceFundingInvestorVO> sfiVOList) {
		this.sfiVOList = sfiVOList;
	}
	
	
}
