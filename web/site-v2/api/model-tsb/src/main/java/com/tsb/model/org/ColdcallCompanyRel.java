package com.tsb.model.org;

import java.util.Date;

public class ColdcallCompanyRel {
	private Integer id;
	private Integer companyId;
	private Integer coldcallId;
	private Date createTime;
	
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getCompanyId() {
		return companyId;
	}
	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}
	public Integer getColdcallId() {
		return coldcallId;
	}
	public void setColdcallId(Integer coldcallId) {
		this.coldcallId = coldcallId;
	}
	public Date getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Date createTime) {
		this.createTime = createTime;
	}
}
