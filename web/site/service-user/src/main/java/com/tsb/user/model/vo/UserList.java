package com.tsb.user.model.vo;

import java.util.List;

public class UserList {
	private Integer userId;
	private List<CompanyListVO> companyListVOList;
	private int listCount;

	public Integer getUserId() {
		return userId;
	}

	public void setUserId(Integer userId) {
		this.userId = userId;
	}

	public List<CompanyListVO> getCompanyListVOList() {
		return companyListVOList;
	}

	public void setCompanyListVOList(List<CompanyListVO> companyListVOList) {
		this.companyListVOList = companyListVOList;
	}
	public int getListCount() {
		return listCount;
	}

	public void setListCount(int listCount) {
		this.listCount = listCount;
	}
}
