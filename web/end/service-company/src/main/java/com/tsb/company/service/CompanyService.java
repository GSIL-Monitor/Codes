package com.tsb.company.service;

import java.util.List;

import com.tsb.company.vo.CompanySearchVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.model.Company;
import com.tsb.model.Funding;
import com.tsb.model.source.SourceCompany;


public interface CompanyService {
	CompanyVO get(String code);
	
	List<CompanySearchVO> getCompaniesByIds(List list);
}
