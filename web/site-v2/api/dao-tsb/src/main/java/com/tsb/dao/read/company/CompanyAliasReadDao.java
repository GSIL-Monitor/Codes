package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.CompanyAlias;

public interface CompanyAliasReadDao {

	List<CompanyAlias> getByCompanyId(Integer companyId);
	CompanyAlias getByName(String name);
	CompanyAlias getByCompanyIdAndName(@Param("companyId") Integer companyId, @Param("name") String name);
}
