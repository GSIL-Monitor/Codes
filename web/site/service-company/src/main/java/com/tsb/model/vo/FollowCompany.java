package com.tsb.model.vo;

import java.util.List;

import com.tsb.model.Company;

public class FollowCompany {
	private Company company;
	private Integer followStatus;
	private String followDate;
	// related column
	private String location;
	// keywords
	private String keywords;
	private List<CompanyTagRelVO> tagRelList;

	public Company getCompany() {
		return company;
	}

	public void setCompany(Company company) {
		this.company = company;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	public Integer getFollowStatus() {
		return followStatus;
	}

	public void setFollowStatus(Integer followStatus) {
		this.followStatus = followStatus;
	}

	public String getFollowDate() {
		return followDate;
	}

	public void setFollowDate(String followDate) {
		this.followDate = followDate;
	}

	public String getKeywords() {
		return keywords;
	}

	public void setKeywords(String keywords) {
		this.keywords = keywords;
	}

	public List<CompanyTagRelVO> getTagRelList() {
		return tagRelList;
	}

	public void setTagRelList(List<CompanyTagRelVO> tagRelList) {
		this.tagRelList = tagRelList;
	}

}
