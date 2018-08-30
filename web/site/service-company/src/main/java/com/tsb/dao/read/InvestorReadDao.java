package com.tsb.dao.read;

import com.tsb.model.Investor;

public interface InvestorReadDao {
	Investor get(int investorId);
}
