package com.tsb.admin.service;

import java.util.List;

import com.tsb.admin.vo.CompanyVO;
import com.tsb.model.Company;
import com.tsb.model.Funding;
import com.tsb.model.source.SourceCompany;


public interface CompanyService {
	Company get(Integer id);
	Company get(String code);
	Integer getLocation(String name);
	List<SourceCompany> getSource(Integer companyId);
	
	void update(Company company);
	void updateFunding(Funding funding);
	
	List<CompanyVO> getCompaniesByIds(List list);
}
