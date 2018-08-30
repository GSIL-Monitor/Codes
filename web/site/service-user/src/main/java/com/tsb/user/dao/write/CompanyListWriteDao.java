package com.tsb.user.dao.write;

import com.tsb.model.user.CompanyList;

public interface CompanyListWriteDao {
	void updateDesc(CompanyList companyList);

	void delete(CompanyList companyList);

	void insert(CompanyList companyList);

	void updateModifyTime(CompanyList companyList);
}
