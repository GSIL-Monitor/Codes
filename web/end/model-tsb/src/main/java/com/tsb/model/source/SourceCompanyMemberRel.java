package com.tsb.model.source;

import java.sql.Date;

public class SourceCompanyMemberRel extends SourceBasicModel {
	private Integer id;
	private Integer companyMemberRelId;
	private Integer sourceCompanyId;
	private Integer sourceMemberId;
	private String position;
	private Date joinDate;
	private Date leaveDate;
	private Integer type;
	
	//********************************
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getCompanyMemberRelId() {
		return companyMemberRelId;
	}
	public void setCompanyMemberRelId(Integer companyMemberRelId) {
		this.companyMemberRelId = companyMemberRelId;
	}
	public Integer getSourceCompanyId() {
		return sourceCompanyId;
	}
	public void setSourceCompanyId(Integer sourceCompanyId) {
		this.sourceCompanyId = sourceCompanyId;
	}
	public Integer getSourceMemberId() {
		return sourceMemberId;
	}
	public void setSourceMemberId(Integer sourceMemberId) {
		this.sourceMemberId = sourceMemberId;
	}
	public String getPosition() {
		return position;
	}
	public void setPosition(String position) {
		this.position = position;
	}
	public Date getJoinDate() {
		return joinDate;
	}
	public void setJoinDate(Date joinDate) {
		this.joinDate = joinDate;
	}
	public Date getLeaveDate() {
		return leaveDate;
	}
	public void setLeaveDate(Date leaveDate) {
		this.leaveDate = leaveDate;
	}
	public Integer getType() {
		return type;
	}
	public void setType(Integer type) {
		this.type = type;
	}
}
