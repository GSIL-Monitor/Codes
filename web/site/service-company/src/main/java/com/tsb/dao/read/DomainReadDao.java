package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.Domain;

public interface DomainReadDao {
	List<Domain> getByCompanyId(Integer companyId);
}
