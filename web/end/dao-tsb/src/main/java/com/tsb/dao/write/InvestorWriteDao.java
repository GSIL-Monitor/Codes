package com.tsb.dao.write;

import com.tsb.model.Investor;

public interface InvestorWriteDao {
	void insert(Investor v);
	void update(Investor v);
}
