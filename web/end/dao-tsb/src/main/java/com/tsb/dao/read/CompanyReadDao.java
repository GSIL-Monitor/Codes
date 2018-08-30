package com.tsb.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.Company;



public interface CompanyReadDao {
	Integer getIdByCode(String code);
	Company getByCode(String code);
	Company getById(Integer id);
	
}
