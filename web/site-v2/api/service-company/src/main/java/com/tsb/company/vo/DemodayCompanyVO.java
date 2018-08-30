package com.tsb.company.vo;

import java.sql.Timestamp;

public class DemodayCompanyVO {

	private String code;
	private String name;
	private String orgName;
	private Integer rank;
	private Integer scoringStatus;
	private Integer joinStatus;
	private Timestamp createTime;

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

	public Timestamp getCreateTime() {
		return createTime;
	}

	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}

}
