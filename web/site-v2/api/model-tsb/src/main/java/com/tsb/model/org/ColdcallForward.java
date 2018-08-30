package com.tsb.model.org;

import java.sql.Timestamp;

public class ColdcallForward {
	private Integer id;
	private Integer coldcallId;
	private Integer fromUserId;
	private Integer toUserId;
	private Timestamp createTime;
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
	public Integer getFromUserId() {
		return fromUserId;
	}
	public void setFromUserId(Integer fromUserId) {
		this.fromUserId = fromUserId;
	}
	public Integer getToUserId() {
		return toUserId;
	}
	public void setToUserId(Integer toUserId) {
		this.toUserId = toUserId;
	}
	public Timestamp getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}
	
}
