package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.Domain;

public interface DomainReadDao {

	List<Domain> getByCompanyId(Integer companyId);
	Domain getByDomain(String domain);
}
