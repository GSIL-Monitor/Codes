package com.tsb.company.service;

import java.util.List;
import java.util.Map;

import com.tsb.company.vo.CompanyDescVO;
import com.tsb.company.vo.CompanySearchVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.model.company.Company;

@SuppressWarnings("rawtypes")
public interface CompanyService {
	CompanyVO get(String code);
	String getName(String code);
	CompanyDescVO getDesc(String code);
	List getGongShang(Integer companyId);
	List<CompanySearchVO> getCompaniesByIds(List list);
	List<CompanySearchVO> getCompaniesByCodes(List list);
	
	void update(CompanyVO update, Integer userId);
	Map create(Company company, Integer userId,Integer source);
}
