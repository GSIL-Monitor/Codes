package com.tsb.model.crowdfunding;

import com.tsb.model.BasicModel;

public class CfLeaderRel extends BasicModel {

	private Integer id;
	private Integer cfId;
	private Integer investorId;
	private String description;
	private Integer investment;
	private Integer currency;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getCfId() {
		return cfId;
	}

	public void setCfId(Integer cfId) {
		this.cfId = cfId;
	}

	public Integer getInvestorId() {
		return investorId;
	}

	public void setInvestorId(Integer investorId) {
		this.investorId = investorId;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Integer getInvestment() {
		return investment;
	}

	public void setInvestment(Integer investment) {
		this.investment = investment;
	}

	public Integer getCurrency() {
		return currency;
	}

	public void setCurrency(Integer currency) {
		this.currency = currency;
	}

}
