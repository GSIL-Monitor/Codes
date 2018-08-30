package com.tsb.dao.write.org;

import com.tsb.model.org.Deal;

public interface DealWriteDao {
	void insert(Deal deal);
	void update(Deal deal);
}
