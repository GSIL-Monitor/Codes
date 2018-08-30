package com.tsb.dao.read.source;

import java.util.List;

import com.tsb.model.source.SourceFundingInvestorRel;

public interface SourceFundingInvestorRelReadDao {
	List<SourceFundingInvestorRel> get(Integer firId);
	
}
