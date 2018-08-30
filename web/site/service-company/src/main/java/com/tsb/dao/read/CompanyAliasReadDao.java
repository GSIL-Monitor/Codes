package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.CompanyAlias;

public interface CompanyAliasReadDao {
	List<CompanyAlias> getByCompanyId(Integer companyId);
}
