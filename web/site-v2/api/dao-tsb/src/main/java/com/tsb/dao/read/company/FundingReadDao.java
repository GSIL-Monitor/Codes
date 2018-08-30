package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.Funding;

public interface FundingReadDao {

	 List<Funding> getByCompanyId(Integer companyId);
	 
	 Funding getById(Integer id);
}
