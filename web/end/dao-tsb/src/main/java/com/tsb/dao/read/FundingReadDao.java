package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.Funding;


public interface FundingReadDao {
	List<Funding> get(Integer companyId); 
	Funding getByFundingId(Integer fundingId); 
}
