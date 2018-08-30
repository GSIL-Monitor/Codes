package com.tsb.model.company;

import java.sql.Date;

import com.tsb.model.BasicModel;

public class Footprint extends BasicModel {

	private Integer id;
	private Integer companyId;
	private Date footDate;
	private String description;

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

	public Date getFootDate() {
		return footDate;
	}

	public void setFootDate(Date footDate) {
		this.footDate = footDate;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

}
