package com.tsb.admin.service;

import java.util.List;
import java.util.Map;

import com.tsb.model.org.Organization;

@SuppressWarnings("rawtypes")
public interface OrgService {

	List getOrgs();
	Map coutOrgUsersInfo(int id);
	Map getOrgUsersInfo(int id);
	Map getOrgUsersInfo(int id,int from,int pageSize);
	
	Organization getOrg(String name);

	void addOrg(Organization org);
	
	void deleteOrg(Integer id);
	
	void update(Organization org);

}
