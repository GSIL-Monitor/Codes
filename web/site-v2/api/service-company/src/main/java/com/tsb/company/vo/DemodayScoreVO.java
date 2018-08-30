package com.tsb.company.vo;

public class DemodayScoreVO {
	// company code
	private String code;
	// company name
	private String name;
	// recommender
	private String orgName;

	private String location;
	private Integer investment;
	private Integer currency;
	// user info and user score
	private String userName;
	private Integer industry;
	private Integer team;
	private Integer product;
	private Integer gain;
	private Integer preMoney;
	private Integer rank;
	private Integer scoringStatus;
	private Integer joinStatus;
	//初筛打的分数
	private Integer preScore;

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

	public String getOrgName() {
		return orgName;
	}

	public void setOrgName(String orgName) {
		this.orgName = orgName;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
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

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public Integer getIndustry() {
		return industry;
	}

	public void setIndustry(Integer industry) {
		this.industry = industry;
	}

	public Integer getTeam() {
		return team;
	}

	public void setTeam(Integer team) {
		this.team = team;
	}

	public Integer getProduct() {
		return product;
	}

	public void setProduct(Integer product) {
		this.product = product;
	}

	public Integer getGain() {
		return gain;
	}

	public void setGain(Integer gain) {
		this.gain = gain;
	}

	public Integer getPreMoney() {
		return preMoney;
	}

	public void setPreMoney(Integer preMoney) {
		this.preMoney = preMoney;
	}

	public Integer getRank() {
		return rank;
	}

	public void setRank(Integer rank) {
		this.rank = rank;
	}

	public Integer getScoringStatus() {
		return scoringStatus;
	}

	public void setScoringStatus(Integer scoringStatus) {
		this.scoringStatus = scoringStatus;
	}

	public Integer getJoinStatus() {
		return joinStatus;
	}

	public void setJoinStatus(Integer joinStatus) {
		this.joinStatus = joinStatus;
	}

	public Integer getPreScore() {
		return preScore;
	}

	public void setPreScore(Integer preScore) {
		this.preScore = preScore;
	}

}
