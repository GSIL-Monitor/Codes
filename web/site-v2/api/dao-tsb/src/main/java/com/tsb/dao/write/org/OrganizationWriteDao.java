package com.tsb.dao.write.org;

import com.tsb.model.org.Organization;

public interface OrganizationWriteDao {
	void insert(Organization org);
	void update(Organization org);
	void delete(Integer id);
}
