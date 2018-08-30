package com.tsb.admin.service;

import com.tsb.model.Investor;

public interface InvestorService {
	void addInvestor(Investor v);
	void updateInvestor(Investor v);
	void deleteInvestor(Integer id);
}
