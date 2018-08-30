package com.tsb.dao.read.org;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.ColdcallCompanyRel;

public interface ColdcallCompanyRelReadDao {
	ColdcallCompanyRel getByCompanyId(int companyId);
	ColdcallCompanyRel getByCompanyIdAndColdcallId(@Param("companyId") int companyId, @Param("coldcallId") int coldcallId);
	Integer getMatchedColdCall();
}
