package com.tsb.dao.write.company;

import com.tsb.model.company.Funding;

public interface FundingWriteDao {
	void insert(Funding funding);
	void update(Funding funding);
	void delete(Integer id);
}
