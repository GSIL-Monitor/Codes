package com.tsb.dao.read.company;

import com.tsb.model.company.Investor;

public interface InvestorReadDao {
	
	Investor getById(int id);

	Investor getByName(String name);
}
