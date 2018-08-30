package com.tsb.model.org;

import java.sql.Timestamp;

public class DealHistory {
	private Integer id;
	private Integer dealId;
	private Integer priority;
	private Integer status;
	private Integer declineStatus;
	private Timestamp createTime;
	private Integer creatorId;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getDealId() {
		return dealId;
	}
	public void setDealId(Integer dealId) {
		this.dealId = dealId;
	}
	public Integer getPriority() {
		return priority;
	}
	public void setPriority(Integer priority) {
		this.priority = priority;
	}
	public Integer getStatus() {
		return status;
	}
	public void setStatus(Integer status) {
		this.status = status;
	}
	public Integer getDeclineStatus() {
		return declineStatus;
	}
	public void setDeclineStatus(Integer declineStatus) {
		this.declineStatus = declineStatus;
	}
	public Timestamp getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}
	public Integer getCreatorId() {
		return creatorId;
	}
	public void setCreatorId(Integer creatorId) {
		this.creatorId = creatorId;
	}
	
}
