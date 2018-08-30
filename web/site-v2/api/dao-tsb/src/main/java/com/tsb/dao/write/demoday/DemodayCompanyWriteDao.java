package com.tsb.dao.write.demoday;

import com.tsb.model.demoday.DemodayCompany;

public interface DemodayCompanyWriteDao {

	void insert(DemodayCompany demodayCompany);

	void update(DemodayCompany demodayCompany);
	
	void delete(Integer id);
}
