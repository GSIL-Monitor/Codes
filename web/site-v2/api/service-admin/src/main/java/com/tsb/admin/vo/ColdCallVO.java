package com.tsb.admin.vo;

import java.sql.Timestamp;

public class ColdCallVO {
	private Integer coldcallId;
	private Integer companyId;
	private Integer dealId;

	private Integer coldcallType;
	private String coldcallName;
	private Timestamp coldcallCreateTime;

	private String companyCode;
	private String companyName;
	private String companyFullName;

	private Integer assigneeId;
	private String assignee;
	private Integer sponsorId;
	private String sponsor;
	private Integer score;

	private Integer declineStatus;

	private Integer orgId;
	private String orgName;

	public Integer getColdcallId() {
		return coldcallId;
	}

	public void setColdcallId(Integer coldcallId) {
		this.coldcallId = coldcallId;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public String getColdcallName() {
		return coldcallName;
	}

	public void setColdcallName(String coldcallName) {
		this.coldcallName = coldcallName;
	}

	public Timestamp getColdcallCreateTime() {
		return coldcallCreateTime;
	}

	public void setColdcallCreateTime(Timestamp coldcallCreateTime) {
		this.coldcallCreateTime = coldcallCreateTime;
	}

	public String getCompanyCode() {
		return companyCode;
	}

	public void setCompanyCode(String companyCode) {
		this.companyCode = companyCode;
	}

	public String getCompanyName() {
		return companyName;
	}

	public void setCompanyName(String companyName) {
		this.companyName = companyName;
	}

	public String getCompanyFullName() {
		return companyFullName;
	}

	public void setCompanyFullName(String companyFullName) {
		this.companyFullName = companyFullName;
	}

	public Integer getAssigneeId() {
		return assigneeId;
	}

	public void setAssigneeId(Integer assigneeId) {
		this.assigneeId = assigneeId;
	}

	public String getAssignee() {
		return assignee;
	}

	public void setAssignee(String assignee) {
		this.assignee = assignee;
	}

	public Integer getSponsorId() {
		return sponsorId;
	}

	public void setSponsorId(Integer sponsorId) {
		this.sponsorId = sponsorId;
	}

	public String getSponsor() {
		return sponsor;
	}

	public void setSponsor(String sponsor) {
		this.sponsor = sponsor;
	}

	public Integer getScore() {
		return score;
	}

	public void setScore(Integer score) {
		this.score = score;
	}

	public Integer getDealId() {
		return dealId;
	}

	public void setDealId(Integer dealId) {
		this.dealId = dealId;
	}

	public Integer getColdcallType() {
		return coldcallType;
	}

	public void setColdcallType(Integer coldcallType) {
		this.coldcallType = coldcallType;
	}

	public Integer getDeclineStatus() {
		return declineStatus;
	}

	public void setDeclineStatus(Integer declineStatus) {
		this.declineStatus = declineStatus;
	}

	public Integer getOrgId() {
		return orgId;
	}

	public void setOrgId(Integer orgId) {
		this.orgId = orgId;
	}

	public String getOrgName() {
		return orgName;
	}

	public void setOrgName(String orgName) {
		this.orgName = orgName;
	}

}
