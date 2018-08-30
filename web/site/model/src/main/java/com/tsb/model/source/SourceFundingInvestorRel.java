package com.tsb.model.source;

public class SourceFundingInvestorRel extends SourceBasicModel{

	private Integer id;
	private Integer sourceFundingId;
	private Integer sourceInvestorId;
	private Integer fundingInvestorRelId;
	private Integer currency;
	private Integer investment;
	private Character precise;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getSourceFundingId() {
		return sourceFundingId;
	}
	public void setSourceFundingId(Integer sourceFundingId) {
		this.sourceFundingId = sourceFundingId;
	}
	public Integer getSourceInvestorId() {
		return sourceInvestorId;
	}
	public void setSourceInvestorId(Integer sourceInvestorId) {
		this.sourceInvestorId = sourceInvestorId;
	}
	public Integer getFundingInvestorRelId() {
		return fundingInvestorRelId;
	}
	public void setFundingInvestorRelId(Integer fundingInvestorRelId) {
		this.fundingInvestorRelId = fundingInvestorRelId;
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
