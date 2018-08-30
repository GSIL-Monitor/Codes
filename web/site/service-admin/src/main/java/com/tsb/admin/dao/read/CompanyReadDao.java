package com.tsb.admin.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;
import org.junit.runners.Parameterized.Parameters;

import com.tsb.admin.vo.CompanyVO;
import com.tsb.model.Company;



public interface CompanyReadDao {
	Integer getIdByCode(String code);
	Company getByCode(String code);
	Company getById(Integer id);
	
	List<CompanyVO> getCompaniesByIds(@Param("companyIds")List companyIds);
}
