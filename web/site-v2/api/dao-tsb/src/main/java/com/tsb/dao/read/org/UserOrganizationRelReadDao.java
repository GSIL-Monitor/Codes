package com.tsb.dao.read.org;

import java.util.List;

import com.tsb.model.org.UserOrganizationRel;

public interface UserOrganizationRelReadDao {
	UserOrganizationRel get(Integer id);
	
	List<Integer> getUserIds(Integer orgId);
	
	List<Integer> getUserIdsByOrgId(Integer orgId);
}
