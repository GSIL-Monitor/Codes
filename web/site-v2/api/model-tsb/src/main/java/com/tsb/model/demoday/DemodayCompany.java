package com.tsb.model.demoday;

import com.tsb.model.TimeModel;

public class DemodayCompany extends TimeModel {

	private Integer id;
	private Integer demodayId;
	private Integer companyId;
	private Integer organizationId;
	private Integer scoringStatus;
	private Integer joinStatus;
	private Integer rank;
	private String recommendation;
	private Character pass;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getDemodayId() {
		return demodayId;
	}

	public void setDemodayId(Integer demodayId) {
		this.demodayId = demodayId;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public Integer getOrganizationId() {
		return organizationId;
	}

	public void setOrganizationId(Integer organizationId) {
		this.organizationId = organizationId;
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

	public Integer getRank() {
		return rank;
	}

	public void setRank(Integer rank) {
		this.rank = rank;
	}

	public String getRecommendation() {
		return recommendation;
	}

	public void setRecommendation(String recommendation) {
		this.recommendation = recommendation;
	}

	public Character getPass() {
		return pass;
	}

	public void setPass(Character pass) {
		this.pass = pass;
	}

}
