package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.Company;

@SuppressWarnings("rawtypes")
public interface CompanyReadDao {

	Company getById(Integer id);
	
	Company getByCode(String code);
	
	Integer getIdByCode(String code);

	List getIdsByCodes(@Param("codeList") List codes);

	List<Company> listByColdcallId(int coldcallId);
	List<Company> listCandidatesByColdcallId(int coldcallId);
	
	List<Company> getByName(String name);
	
	List<Company> getByFullName(String name);
	
	List<Company> getByIds(@Param("ids") List ids);
}
