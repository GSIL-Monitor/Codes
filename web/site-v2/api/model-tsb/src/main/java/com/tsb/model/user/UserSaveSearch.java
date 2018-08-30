package com.tsb.model.user;

import com.tsb.model.BasicModel;

public class UserSaveSearch extends BasicModel {

	private Integer id;
	private Integer userId;
	private String params;

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

	public String getParams() {
		return params;
	}

	public void setParams(String params) {
		this.params = params;
	}

}
