package com.tsb.model.user;

import java.io.Serializable;

import com.tsb.model.BasicModel;

public class UserCompanyNote extends BasicModel implements Serializable {

	private static final long serialVersionUID = -8239148956181177002L;

	private Integer id;
	private Integer userId;
	private Integer companyId;
	private String note;

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

	public String getNote() {
		return note;
	}

	public void setNote(String note) {
		this.note = note;
	}

}
