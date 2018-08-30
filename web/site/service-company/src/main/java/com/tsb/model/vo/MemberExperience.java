package com.tsb.model.vo;

import com.tsb.model.CompanyMemberRel;

public class MemberExperience {
	private String companyCode;
	private String companyName;
	private String companyFullName;
	private String companyLogo;
	private CompanyMemberRel companyMemberRel;

	public String getCompanyCode() {
		return companyCode;
	}

	public void setCompanyCode(String companyCode) {
		this.companyCode = companyCode;
	}

	public String getCompanyName() {
		return companyName;
	}

	public void setCompanyName(String companyName) {
		this.companyName = companyName;
	}

	public String getCompanyFullName() {
		return companyFullName;
	}

	public void setCompanyFullName(String companyFullName) {
		this.companyFullName = companyFullName;
	}

	public String getCompanyLogo() {
		return companyLogo;
	}

	public void setCompanyLogo(String companyLogo) {
		this.companyLogo = companyLogo;
	}

	public CompanyMemberRel getCompanyMemberRel() {
		return companyMemberRel;
	}

	public void setCompanyMemberRel(CompanyMemberRel companyMemberRel) {
		this.companyMemberRel = companyMemberRel;
	}

}
