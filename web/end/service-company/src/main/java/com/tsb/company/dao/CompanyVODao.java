package com.tsb.company.dao;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.company.vo.CompanyVO;

public interface CompanyVODao {
	List getSearch(@Param("companyIds")List companyIds);
	CompanyVO getByCode(String code);
}
