package com.tsb.dao.write.demoday;

import com.tsb.model.demoday.DemodayOrganization;

public interface DemodayOrganizationWriteDao {
	void insert(DemodayOrganization demodayOrganization);

	void update(DemodayOrganization demodayOrganization);
	
	void delete(Integer orgId);
}
