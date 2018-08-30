package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class CompaniesRel extends BasicModel {

	private Integer id;
	private Integer companyId;
	private Integer company2Id;
	private Float distance;

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

	public Integer getCompany2Id() {
		return company2Id;
	}

	public void setCompany2Id(Integer company2Id) {
		this.company2Id = company2Id;
	}

	public Float getDistance() {
		return distance;
	}

	public void setDistance(Float distance) {
		this.distance = distance;
	}

}
