package com.tsb.model;

import java.sql.Date;
import java.util.List;


public class Funding extends BasicModel {
	private Integer id;
	private Integer companyId;
	private Integer preMoney;
	private Integer postMoney;
	private Integer investment;
	private Integer round;
	private String roundDesc;
	private Integer currency;
	private Character precise;
	private Date fundingDate;
	private Integer fundingType;
	private List<FundingInvestorRel> investorList;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public Integer getPreMoney() {
		return preMoney;
	}

	public void setPreMoney(Integer preMoney) {
		this.preMoney = preMoney;
	}

	public Integer getPostMoney() {
		return postMoney;
	}

	public void setPostMoney(Integer postMoney) {
		this.postMoney = postMoney;
	}

	public Integer getInvestment() {
		return investment;
	}

	public void setInvestment(Integer investment) {
		this.investment = investment;
	}

	public Integer getRound() {
		return round;
	}

	public void setRound(Integer round) {
		this.round = round;
	}

	public String getRoundDesc() {
		return roundDesc;
	}

	public void setRoundDesc(String roundDesc) {
		this.roundDesc = roundDesc;
	}

	public Integer getCurrency() {
		return currency;
	}

	public void setCurrency(Integer currency) {
		this.currency = currency;
	}

	public Character getPrecise() {
		return precise;
	}

	public void setPrecise(Character precise) {
		this.precise = precise;
	}

	public Date getFundingDate() {
		return fundingDate;
	}

	public void setFundingDate(Date fundingDate) {
		this.fundingDate = fundingDate;
	}

	public Integer getFundingType() {
		return fundingType;
	}

	public void setFundingType(Integer fundingType) {
		this.fundingType = fundingType;
	}

	public List<FundingInvestorRel> getInvestorList() {
		return investorList;
	}

	public void setInvestorList(List<FundingInvestorRel> investorList) {
		this.investorList = investorList;
	}

}
