package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.CompanyMemberRel;

public interface CompanyMemberRelReadDao {

	List<CompanyMemberRel> get(Integer companyId);

	int count(int companyId);

	CompanyMemberRel listByCompanyId(Integer id);

	CompanyMemberRel listByMemberId(Integer id);
}
