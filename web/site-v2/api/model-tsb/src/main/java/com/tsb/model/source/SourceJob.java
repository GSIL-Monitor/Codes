package com.tsb.model.source;

import java.sql.Date;

public class SourceJob extends SourceBasicModel {

	private Integer id;
	private Integer sourceCompanyId;
	private Integer jobId;
	private String position;
	private String salary;
	private String description;
	private Integer domain;
	private Integer locationId;
	private Integer educationType;
	private Integer workYearType;
	private Date startDate;
	private Date updateDate;
	private String sourceId;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getSourceCompanyId() {
		return sourceCompanyId;
	}

	public void setSourceCompanyId(Integer sourceCompanyId) {
		this.sourceCompanyId = sourceCompanyId;
	}

	public Integer getJobId() {
		return jobId;
	}

	public void setJobId(Integer jobId) {
		this.jobId = jobId;
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

	public Integer getWorkYearType() {
		return workYearType;
	}

	public void setWorkYearType(Integer workYearType) {
		this.workYearType = workYearType;
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

	public String getSourceId() {
		return sourceId;
	}

	public void setSourceId(String sourceId) {
		this.sourceId = sourceId;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

}
