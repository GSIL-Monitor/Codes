package com.tsb.dao.write;

import com.tsb.model.CompanyMemberRel;

public interface CompanyMemberRelWriteDao {
	void update(CompanyMemberRel rel);
	void delete(Integer id);
}
