package com.tsb.model.user;

import java.io.Serializable;

import com.tsb.model.BasicModel;

public class CompanyListRel extends BasicModel implements Serializable {

	private static final long serialVersionUID = 126323159153707278L;

	private Integer id;
	private Integer companyId;
	private Integer companyListId;
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
	public Integer getCompanyListId() {
		return companyListId;
	}
	public void setCompanyListId(Integer companyListId) {
		this.companyListId = companyListId;
	}


}
