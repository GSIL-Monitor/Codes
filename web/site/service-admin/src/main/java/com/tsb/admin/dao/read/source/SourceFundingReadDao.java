package com.tsb.admin.dao.read.source;

import java.util.List;

import com.tsb.model.source.SourceCompany;
import com.tsb.model.source.SourceFunding;

public interface SourceFundingReadDao {
	List<SourceFunding> getByFundingId(Integer fundingId);
}
