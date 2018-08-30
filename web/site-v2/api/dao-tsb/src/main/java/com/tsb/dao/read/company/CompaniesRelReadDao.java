package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.CompaniesRel;

public interface CompaniesRelReadDao {
	List<CompaniesRel> get(Integer companyId);
}
