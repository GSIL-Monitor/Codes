package com.tsb.model;

public class CompanyAlias extends BasicModel {
	private Integer id;
	private Integer companyId;
	private String name;
	private Integer type;
	private Character verify;

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

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

	public Character getVerify() {
		return verify;
	}

	public void setVerify(Character verify) {
		this.verify = verify;
	}

}
