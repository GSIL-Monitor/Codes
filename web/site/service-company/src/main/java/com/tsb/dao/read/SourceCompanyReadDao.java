package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.source.SourceCompany;


public interface SourceCompanyReadDao {
	List<SourceCompany> getByCompanyId(Integer companyId);
}
