package com.tsb.dao.read.source;

import java.util.List;

import com.tsb.model.source.SourceInvestor;

public interface SourceInvestorReadDao {
	SourceInvestor getById(Integer id);
	List<SourceInvestor> listByInvestorId(Integer id);
}
