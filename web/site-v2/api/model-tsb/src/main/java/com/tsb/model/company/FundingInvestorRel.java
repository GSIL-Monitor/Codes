package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class FundingInvestorRel extends BasicModel {

	private Integer id;
	private Integer fundingId;
	private Integer investorId;
	private Integer currency;
	private Integer investment;
	private Character precise;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getFundingId() {
		return fundingId;
	}

	public void setFundingId(Integer fundingId) {
		this.fundingId = fundingId;
	}

	public Integer getInvestorId() {
		return investorId;
	}

	public void setInvestorId(Integer investorId) {
		this.investorId = investorId;
	}

	public Integer getCurrency() {
		return currency;
	}

	public void setCurrency(Integer currency) {
		this.currency = currency;
	}

	public Integer getInvestment() {
		return investment;
	}

	public void setInvestment(Integer investment) {
		this.investment = investment;
	}

	public Character getPrecise() {
		return precise;
	}

	public void setPrecise(Character precise) {
		this.precise = precise;
	}

}
