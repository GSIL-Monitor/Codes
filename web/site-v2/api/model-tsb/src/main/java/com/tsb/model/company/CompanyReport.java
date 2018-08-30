package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class CompanyReport extends BasicModel {

	private Integer id;
	private Integer companyId;
	private String recruitSummary;
	private String recruitDistribution;
	private String businessData;
	private String reportSummary;
	private String reportFocus;

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

	public String getRecruitSummary() {
		return recruitSummary;
	}

	public void setRecruitSummary(String recruitSummary) {
		this.recruitSummary = recruitSummary;
	}

	public String getRecruitDistribution() {
		return recruitDistribution;
	}

	public void setRecruitDistribution(String recruitDistribution) {
		this.recruitDistribution = recruitDistribution;
	}

	public String getBusinessData() {
		return businessData;
	}

	public void setBusinessData(String businessData) {
		this.businessData = businessData;
	}

	public String getReportSummary() {
		return reportSummary;
	}

	public void setReportSummary(String reportSummary) {
		this.reportSummary = reportSummary;
	}

	public String getReportFocus() {
		return reportFocus;
	}

	public void setReportFocus(String reportFocus) {
		this.reportFocus = reportFocus;
	}

}
