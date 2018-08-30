package com.tsb.company.vo;

public class DemodayPreScoreVO {
	// company code
	private String code;
	// company name
	private String name;
	// recommender
	private String orgName;

	private String location;
	private Integer investment;
	private Integer currency;
	private Integer score;
	private Integer rank;
	private Integer scoringStatus;
	private Integer joinStatus;

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

	public Integer getScore() {
		return score;
	}

	public void setScore(Integer score) {
		this.score = score;
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

}
