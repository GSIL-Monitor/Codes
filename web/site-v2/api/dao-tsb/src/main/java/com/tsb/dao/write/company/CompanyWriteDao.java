package com.tsb.dao.write.company;

import com.tsb.model.company.Company;

public interface CompanyWriteDao {
	void insert(Company company);
	void update(Company company);
}
