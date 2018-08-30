package com.tsb.model.user;

import java.sql.Timestamp;

public class Recommendation {
	private Integer id;
	private Integer userId;
	private Integer companyId;
	private Float confidence;
	private Timestamp createTime;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getUserId() {
		return userId;
	}
	public void setUserId(Integer userId) {
		this.userId = userId;
	}
	public Integer getCompanyId() {
		return companyId;
	}
	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}
	public Float getConfidence() {
		return confidence;
	}
	public void setConfidence(Float confidence) {
		this.confidence = confidence;
	}
	public Timestamp getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}
	
	
}
