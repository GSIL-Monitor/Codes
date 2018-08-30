package com.tsb.model.company;

import java.sql.Timestamp;

public class Homepage {

	private Integer id;
	private Integer companyId;
	private String originalHomepage;
	private String lastHomepage;
	private Integer status;
	private Timestamp createTime;
	private Timestamp modifyTime;

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

	public String getOriginalHomepage() {
		return originalHomepage;
	}

	public void setOriginalHomepage(String originalHomepage) {
		this.originalHomepage = originalHomepage;
	}

	public String getLastHomepage() {
		return lastHomepage;
	}

	public void setLastHomepage(String lastHomepage) {
		this.lastHomepage = lastHomepage;
	}

	public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}

	public Timestamp getCreateTime() {
		return createTime;
	}

	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}

	public Timestamp getModifyTime() {
		return modifyTime;
	}

	public void setModifyTime(Timestamp modifyTime) {
		this.modifyTime = modifyTime;
	}

}
