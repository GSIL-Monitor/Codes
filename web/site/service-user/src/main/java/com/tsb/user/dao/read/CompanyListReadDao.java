package com.tsb.user.dao.read;

import com.tsb.model.user.CompanyList;

public interface CompanyListReadDao {
	CompanyList get(int id);
	CompanyList getByName(String name);
	int getIdByName(String name);
}
