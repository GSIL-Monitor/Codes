package com.tsb.model.vo;

import com.tsb.model.user.UserCompanyFollow;

public class CompanyHeadVO {
	private Integer companyId;
	private String companyCode;
	private String name;
	private String logo;
	private Character verify;
	private int teamCount;
	private int jobCount;
	private int relCount;
	private int newsCount;
	private UserCompanyFollow userCompanyFollow;

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public String getCompanyCode() {
		return companyCode;
	}

	public void setCompanyCode(String companyCode) {
		this.companyCode = companyCode;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getLogo() {
		return logo;
	}

	public void setLogo(String logo) {
		this.logo = logo;
	}

	public Character getVerify() {
		return verify;
	}

	public void setVerify(Character verify) {
		this.verify = verify;
	}

	public int getTeamCount() {
		return teamCount;
	}

	public void setTeamCount(int teamCount) {
		this.teamCount = teamCount;
	}

	public int getJobCount() {
		return jobCount;
	}

	public void setJobCount(int jobCount) {
		this.jobCount = jobCount;
	}

	public int getRelCount() {
		return relCount;
	}

	public void setRelCount(int relCount) {
		this.relCount = relCount;
	}

	public int getNewsCount() {
		return newsCount;
	}

	public void setNewsCount(int newsCount) {
		this.newsCount = newsCount;
	}

	public UserCompanyFollow getUserCompanyFollow() {
		return userCompanyFollow;
	}

	public void setUserCompanyFollow(UserCompanyFollow userCompanyFollow) {
		this.userCompanyFollow = userCompanyFollow;
	}

}
