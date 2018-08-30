package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class InvestorTagRel extends BasicModel {

	private Integer id;
	private Integer investorId;
	private Integer tagId;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getInvestorId() {
		return investorId;
	}

	public void setInvestorId(Integer investorId) {
		this.investorId = investorId;
	}

	public Integer getTagId() {
		return tagId;
	}

	public void setTagId(Integer tagId) {
		this.tagId = tagId;
	}

}
