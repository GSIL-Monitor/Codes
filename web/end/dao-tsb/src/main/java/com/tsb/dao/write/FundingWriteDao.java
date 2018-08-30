package com.tsb.dao.write;

import com.tsb.model.Funding;

public interface FundingWriteDao {
	Integer insert(Funding funding);
	void update(Funding funding);
}
