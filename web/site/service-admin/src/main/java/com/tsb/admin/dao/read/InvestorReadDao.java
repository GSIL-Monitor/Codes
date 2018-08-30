package com.tsb.admin.dao.read;

import com.tsb.model.Investor;

public interface InvestorReadDao {
	Investor getById(Integer id);
	Investor getByName(String name);
}
