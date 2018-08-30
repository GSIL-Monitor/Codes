package com.tsb.model.company;

import java.sql.Date;

import com.tsb.model.BasicModel;

public class GongShangBase extends BasicModel {

	private Integer id;
	private Integer companyAliasId;
	private String name;
	private String regCapital;
	private String industry;
	private String regInstitute;
	private Date establishDate;
	private String base;
	private String regNumber;
	private String regStatus;
	private Date fromTime;
	private Date toTime;
	private String businessScope;
	private String regLocation;
	private String companyOrgType;
	private String legalPersonId;
	private String legalPersonName;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getCompanyAliasId() {
		return companyAliasId;
	}

	public void setCompanyAliasId(Integer companyAliasId) {
		this.companyAliasId = companyAliasId;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getRegCapital() {
		return regCapital;
	}

	public void setRegCapital(String regCapital) {
		this.regCapital = regCapital;
	}

	public String getIndustry() {
		return industry;
	}

	public void setIndustry(String industry) {
		this.industry = industry;
	}

	public String getRegInstitute() {
		return regInstitute;
	}

	public void setRegInstitute(String regInstitute) {
		this.regInstitute = regInstitute;
	}

	public Date getEstablishDate() {
		return establishDate;
	}

	public void setEstablishDate(Date establishDate) {
		this.establishDate = establishDate;
	}

	public String getBase() {
		return base;
	}

	public void setBase(String base) {
		this.base = base;
	}

	public String getRegNumber() {
		return regNumber;
	}

	public void setRegNumber(String regNumber) {
		this.regNumber = regNumber;
	}

	public String getRegStatus() {
		return regStatus;
	}

	public void setRegStatus(String regStatus) {
		this.regStatus = regStatus;
	}

	public Date getFromTime() {
		return fromTime;
	}

	public void setFromTime(Date fromTime) {
		this.fromTime = fromTime;
	}

	public Date getToTime() {
		return toTime;
	}

	public void setToTime(Date toTime) {
		this.toTime = toTime;
	}

	public String getBusinessScope() {
		return businessScope;
	}

	public void setBusinessScope(String businessScope) {
		this.businessScope = businessScope;
	}

	public String getRegLocation() {
		return regLocation;
	}

	public void setRegLocation(String regLocation) {
		this.regLocation = regLocation;
	}

	public String getCompanyOrgType() {
		return companyOrgType;
	}

	public void setCompanyOrgType(String companyOrgType) {
		this.companyOrgType = companyOrgType;
	}

	public String getLegalPersonId() {
		return legalPersonId;
	}

	public void setLegalPersonId(String legalPersonId) {
		this.legalPersonId = legalPersonId;
	}

	public String getLegalPersonName() {
		return legalPersonName;
	}

	public void setLegalPersonName(String legalPersonName) {
		this.legalPersonName = legalPersonName;
	}

}
