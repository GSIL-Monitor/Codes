package com.tsb.model.org;

public class ColdcallSourceCompanyRel {
	private Integer id;
	private Integer coldcallId;
	private Integer sourceCompanyId;
	
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getColdcallId() {
		return coldcallId;
	}
	public void setColdcallId(Integer coldcallId) {
		this.coldcallId = coldcallId;
	}
	public Integer getSourceCompanyId() {
		return sourceCompanyId;
	}
	public void setSourceCompanyId(Integer sourceCompanyId) {
		this.sourceCompanyId = sourceCompanyId;
	}
}
