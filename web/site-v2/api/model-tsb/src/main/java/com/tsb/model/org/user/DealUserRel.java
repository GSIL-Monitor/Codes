package com.tsb.model.org.user;

import com.tsb.model.TimeModel;

public class DealUserRel extends TimeModel {
	private Integer id;
	private Integer userId;
	private Integer dealId;
	private Integer userIdentify;
	private Integer type;

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

	public Integer getDealId() {
		return dealId;
	}

	public void setDealId(Integer dealId) {
		this.dealId = dealId;
	}

	public Integer getUserIdentify() {
		return userIdentify;
	}

	public void setUserIdentify(Integer userIdentify) {
		this.userIdentify = userIdentify;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

}
