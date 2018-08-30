package com.tsb.model.company;

import java.sql.Date;

import com.tsb.model.BasicModel;

public class Company extends BasicModel {

	private Integer id;
	private String code;
	private String name;
	private String fullName;
	private String description;
	private String productDesc;
	private String modelDesc;
	private String operationDesc;
	private String teamDesc;
	private String marketDesc;
	private String compititorDesc;
	private String advantageDesc;
	private String planDesc;
	private String brief;
	private Integer round;
	private String roundDesc;
	private Integer companyStatus;
	private Integer fundingType;
	private Integer currentRound;
	private String currentRoundDesc;
	private Integer preMoney;
	private Integer postMoney;
	private float shareRatio;
	private Integer investment;
	private Integer currency;
	private Integer headCountMin;
	private Integer headCountMax;
	private Integer locationId;
	private String address;
	private String phone;
	private Date establishDate;
	private String logo;
	private Integer type;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public String getCode() {
		return code;
	}

	public void setCode(String code) {
		this.code = code;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getBrief() {
		return brief;
	}

	public void setBrief(String brief) {
		this.brief = brief;
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

	public Integer getCompanyStatus() {
		return companyStatus;
	}

	public void setCompanyStatus(Integer companyStatus) {
		this.companyStatus = companyStatus;
	}

	public Integer getFundingType() {
		return fundingType;
	}

	public void setFundingType(Integer fundingType) {
		this.fundingType = fundingType;
	}

	public Integer getPreMoney() {
		return preMoney;
	}

	public void setPreMoney(Integer preMoney) {
		this.preMoney = preMoney;
	}

	public Integer getCurrency() {
		return currency;
	}

	public void setCurrency(Integer currency) {
		this.currency = currency;
	}

	public Integer getHeadCountMin() {
		return headCountMin;
	}

	public void setHeadCountMin(Integer headCountMin) {
		this.headCountMin = headCountMin;
	}

	public Integer getHeadCountMax() {
		return headCountMax;
	}

	public void setHeadCountMax(Integer headCountMax) {
		this.headCountMax = headCountMax;
	}

	public Integer getLocationId() {
		return locationId;
	}

	public void setLocationId(Integer locationId) {
		this.locationId = locationId;
	}

	public String getAddress() {
		return address;
	}

	public void setAddress(String address) {
		this.address = address;
	}

	public String getPhone() {
		return phone;
	}

	public void setPhone(String phone) {
		this.phone = phone;
	}

	public Date getEstablishDate() {
		return establishDate;
	}

	public void setEstablishDate(Date establishDate) {
		this.establishDate = establishDate;
	}

	public String getLogo() {
		return logo;
	}

	public void setLogo(String logo) {
		this.logo = logo;
	}

	public Integer getInvestment() {
		return investment;
	}

	public void setInvestment(Integer investment) {
		this.investment = investment;
	}

	public Integer getPostMoney() {
		return postMoney;
	}

	public void setPostMoney(Integer postMoney) {
		this.postMoney = postMoney;
	}

	public float getShareRatio() {
		return shareRatio;
	}

	public void setShareRatio(float shareRatio) {
		this.shareRatio = shareRatio;
	}

	public Integer getCurrentRound() {
		return currentRound;
	}

	public void setCurrentRound(Integer currentRound) {
		this.currentRound = currentRound;
	}

	public String getCurrentRoundDesc() {
		return currentRoundDesc;
	}

	public void setCurrentRoundDesc(String currentRoundDesc) {
		this.currentRoundDesc = currentRoundDesc;
	}

	public String getProductDesc() {
		return productDesc;
	}

	public void setProductDesc(String productDesc) {
		this.productDesc = productDesc;
	}

	public String getModelDesc() {
		return modelDesc;
	}

	public void setModelDesc(String modelDesc) {
		this.modelDesc = modelDesc;
	}

	public String getOperationDesc() {
		return operationDesc;
	}

	public void setOperationDesc(String operationDesc) {
		this.operationDesc = operationDesc;
	}

	public String getTeamDesc() {
		return teamDesc;
	}

	public void setTeamDesc(String teamDesc) {
		this.teamDesc = teamDesc;
	}

	public String getMarketDesc() {
		return marketDesc;
	}

	public void setMarketDesc(String marketDesc) {
		this.marketDesc = marketDesc;
	}

	public String getCompititorDesc() {
		return compititorDesc;
	}

	public void setCompititorDesc(String compititorDesc) {
		this.compititorDesc = compititorDesc;
	}

	public String getAdvantageDesc() {
		return advantageDesc;
	}

	public void setAdvantageDesc(String advantageDesc) {
		this.advantageDesc = advantageDesc;
	}

	public String getPlanDesc() {
		return planDesc;
	}

	public void setPlanDesc(String planDesc) {
		this.planDesc = planDesc;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

}
