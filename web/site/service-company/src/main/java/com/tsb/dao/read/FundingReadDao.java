package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.Funding;

public interface FundingReadDao {
	List<Funding> getByCompanyId(Integer companyId);
}
