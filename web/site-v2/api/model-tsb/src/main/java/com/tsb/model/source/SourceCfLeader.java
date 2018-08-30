package com.tsb.model.source;

import com.tsb.model.BasicModel;

public class SourceCfLeader extends BasicModel {

	private Integer id;
	private Integer sourceCfId;
	private String investorName;
	private String investorType;
	private Integer sourceInvestorId;
	private String description;
	private Integer investment;
	private String valuation;
	private String businessDesc;
	private String reason;
	private String risk;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getSourceCfId() {
		return sourceCfId;
	}

	public void setSourceCfId(Integer sourceCfId) {
		this.sourceCfId = sourceCfId;
	}

	public String getInvestorName() {
		return investorName;
	}

	public void setInvestorName(String investorName) {
		this.investorName = investorName;
	}

	public String getInvestorType() {
		return investorType;
	}

	public void setInvestorType(String investorType) {
		this.investorType = investorType;
	}

	public Integer getSourceInvestorId() {
		return sourceInvestorId;
	}

	public void setSourceInvestorId(Integer sourceInvestorId) {
		this.sourceInvestorId = sourceInvestorId;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getValuation() {
		return valuation;
	}

	public void setValuation(String valuation) {
		this.valuation = valuation;
	}

	public String getBusinessDesc() {
		return businessDesc;
	}

	public void setBusinessDesc(String businessDesc) {
		this.businessDesc = businessDesc;
	}

	public String getReason() {
		return reason;
	}

	public void setReason(String reason) {
		this.reason = reason;
	}

	public String getRisk() {
		return risk;
	}

	public void setRisk(String risk) {
		this.risk = risk;
	}

	public Integer getInvestment() {
		return investment;
	}

	public void setInvestment(Integer investment) {
		this.investment = investment;
	}

}
