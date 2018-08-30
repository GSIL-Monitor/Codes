package com.tsb.model.org.user;

import com.tsb.model.TimeModel;

public class ColdcallUserRel extends TimeModel{
	private Integer id;
	private Integer coldcallId;
	private Integer userId;
	private Integer userIdentify;
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
	public Integer getUserId() {
		return userId;
	}
	public void setUserId(Integer userId) {
		this.userId = userId;
	}
	public Integer getUserIdentify() {
		return userIdentify;
	}
	public void setUserIdentify(Integer userIdentify) {
		this.userIdentify = userIdentify;
	}
}
