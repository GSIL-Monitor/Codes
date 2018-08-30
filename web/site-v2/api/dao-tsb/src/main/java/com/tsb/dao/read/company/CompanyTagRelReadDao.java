package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.CompanyTagRel;

public interface CompanyTagRelReadDao {

	List<CompanyTagRel> getByCompanyId(Integer companyId);
	CompanyTagRel getByCompanyIdAndTagId(@Param("companyId")Integer companyId, @Param("tagId")Integer tagId);
}
