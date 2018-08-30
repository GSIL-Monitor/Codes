package com.tsb.model.vo;

public class CfHeadVO {
	private Integer cfId;
	private Integer companyId;
	private String cfName;
	private int scfLeaderCount;
	private int scfMemberCount;

	public Integer getCfId() {
		return cfId;
	}

	public void setCfId(Integer cfId) {
		this.cfId = cfId;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public String getCfName() {
		return cfName;
	}

	public void setCfName(String cfName) {
		this.cfName = cfName;
	}

	public int getScfLeaderCount() {
		return scfLeaderCount;
	}

	public void setScfLeaderCount(int scfLeaderCount) {
		this.scfLeaderCount = scfLeaderCount;
	}

	public int getScfMemberCount() {
		return scfMemberCount;
	}

	public void setScfMemberCount(int scfMemberCount) {
		this.scfMemberCount = scfMemberCount;
	}

}
