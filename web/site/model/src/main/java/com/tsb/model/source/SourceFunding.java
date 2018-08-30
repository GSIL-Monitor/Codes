package com.tsb.model.source;

import java.sql.Date;

public class SourceFunding extends SourceBasicModel{
	private Integer id;
	private Integer sourceCompanyId;
	private Integer fundingId;
	private Integer preMoney;
	private Integer postMoney;
	private Integer investment;
	private Integer round;
	private String roundDesc;
	private Integer currency;
	private Character precise;
	private Date fundingDate;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getSourceCompanyId() {
		return sourceCompanyId;
	}
	public void setSourceCompanyId(Integer sourceCompanyId) {
		this.sourceCompanyId = sourceCompanyId;
	}
	public Integer getFundingId() {
		return fundingId;
	}
	public void setFundingId(Integer fundingId) {
		this.fundingId = fundingId;
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
	
	
}
