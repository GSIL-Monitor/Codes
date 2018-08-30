package com.tsb.dao.write.org;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.UserOrganizationRel;

public interface UserOrganizationRelWriteDao {
	void delete(Integer orgId);
	
	void insert(UserOrganizationRel userOrgRel);
	
	void deleteById(@Param("orgId")Integer orgId,@Param("userId") Integer userId);
}
