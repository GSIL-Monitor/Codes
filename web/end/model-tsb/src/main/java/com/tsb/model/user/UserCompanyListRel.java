package com.tsb.model.user;

import java.io.Serializable;

import com.tsb.model.BasicModel;

public class UserCompanyListRel extends BasicModel implements Serializable {
	
	private static final long serialVersionUID = -1080384089632680474L;

	private Integer id;
	private Integer userId;
	private Integer companyListId;

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

	public Integer getCompanyListId() {
		return companyListId;
	}

	public void setCompanyListId(Integer companyListId) {
		this.companyListId = companyListId;
	}

}
