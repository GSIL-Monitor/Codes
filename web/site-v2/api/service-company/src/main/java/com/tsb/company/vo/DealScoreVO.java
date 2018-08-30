package com.tsb.company.vo;

import java.util.Date;

public class DealScoreVO {
	private Integer dealId;
	private String companyCode;
	private String companyName;
	private String companyFullName;
	private	Integer assigneeId;
	private String assignee;
	private Date 	assignTime;
	private Integer score;
	
	
	public Integer getDealId() {
		return dealId;
	}
	public void setDealId(Integer dealId) {
		this.dealId = dealId;
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
	public Date getAssignTime() {
		return assignTime;
	}
	public void setAssignTime(Date assignTime) {
		this.assignTime = assignTime;
	}
	public Integer getScore() {
		return score;
	}
	public void setScore(Integer score) {
		this.score = score;
	}
}
