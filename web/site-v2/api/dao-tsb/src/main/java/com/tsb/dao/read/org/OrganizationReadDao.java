package com.tsb.dao.read.org;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.Organization;

public interface OrganizationReadDao {
	Organization get(Integer id);

	Organization getByUser(Integer userId);

	List<Integer> getIdsByNames(@Param("names")List<String> names);

	List<String> getByIds(@Param("ids") List<Integer> ids);
	
	List<Organization> getOrgs();
	
	List<Organization> getXOrgs(Integer status);
	
	Organization getOrgByName(String name);
}
