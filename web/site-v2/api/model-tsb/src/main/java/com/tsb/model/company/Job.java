package com.tsb.model.company;

import java.sql.Date;

import com.tsb.model.BasicModel;

public class Job extends BasicModel {

	private Integer id;
	private Integer companyId;
	private String position;
	private String salary;
	private String description;
	private Integer domain;
	private Integer locationId;
	private Integer educationType;
	private Integer workyearType;
	private Date startDate;
	private Date updateDate;

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

	public String getPosition() {
		return position;
	}

	public void setPosition(String position) {
		this.position = position;
	}

	public String getSalary() {
		return salary;
	}

	public void setSalary(String salary) {
		this.salary = salary;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Integer getDomain() {
		return domain;
	}

	public void setDomain(Integer domain) {
		this.domain = domain;
	}

	public Integer getLocationId() {
		return locationId;
	}

	public void setLocationId(Integer locationId) {
		this.locationId = locationId;
	}

	public Integer getEducationType() {
		return educationType;
	}

	public void setEducationType(Integer educationType) {
		this.educationType = educationType;
	}

	public Integer getWorkyearType() {
		return workyearType;
	}

	public void setWorkyearType(Integer workyearType) {
		this.workyearType = workyearType;
	}

	public Date getStartDate() {
		return startDate;
	}

	public void setStartDate(Date startDate) {
		this.startDate = startDate;
	}

	public Date getUpdateDate() {
		return updateDate;
	}

	public void setUpdateDate(Date updateDate) {
		this.updateDate = updateDate;
	}

}
