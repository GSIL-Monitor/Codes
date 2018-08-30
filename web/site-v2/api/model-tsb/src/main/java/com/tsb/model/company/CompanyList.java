package com.tsb.model.company;

import java.io.Serializable;

import com.tsb.model.BasicModel;

public class CompanyList extends BasicModel implements Serializable {

	private static final long serialVersionUID = 6622475736192094719L;

	private Integer id;
	private String name;
	private String description;
	private Integer status;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}

}
