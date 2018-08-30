package com.tsb.service;

import java.util.List;

public interface CompanyListService {
	@SuppressWarnings("rawtypes")
	void createCompanyListRel(List listIdList, List companyIdList);
}
