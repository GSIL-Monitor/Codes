package com.tsb.dao.read.org;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.Deal;

public interface DealReadDao {
	Deal get(Integer id);
	Deal getByOrganization(@Param("companyId") Integer companyId, @Param("organizationId") Integer organizationId);
}
