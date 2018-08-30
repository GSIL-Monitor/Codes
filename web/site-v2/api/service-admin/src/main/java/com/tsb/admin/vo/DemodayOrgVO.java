package com.tsb.admin.vo;

public class DemodayOrgVO {
	private Integer orgId;
	private String orgName;
	// 是否来参加
	private Integer status;
	private Integer orgStatus;

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

	public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}

	public Integer getOrgStatus() {
		return orgStatus;
	}

	public void setOrgStatus(Integer orgStatus) {
		this.orgStatus = orgStatus;
	}

}
