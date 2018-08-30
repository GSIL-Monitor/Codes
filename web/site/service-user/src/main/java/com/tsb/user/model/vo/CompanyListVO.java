package com.tsb.user.model.vo;

import java.util.List;

import com.tsb.model.user.CompanyList;
import com.tsb.model.user.CompanyListRel;

public class CompanyListVO {
	private CompanyList companyList;
	private List<CompanyListRel> companyListRelList;
	// the number of CompanyListRel
	private int companyCount;

	public CompanyList getCompanyList() {
		return companyList;
	}

	public void setCompanyList(CompanyList companyList) {
		this.companyList = companyList;
	}

	public List<CompanyListRel> getCompanyListRelList() {
		return companyListRelList;
	}

	public void setCompanyListRelList(List<CompanyListRel> companyListRelList) {
		this.companyListRelList = companyListRelList;
	}

	public int getCompanyCount() {
		return companyCount;
	}

	public void setCompanyCount(int companyCount) {
		this.companyCount = companyCount;
	}

}
