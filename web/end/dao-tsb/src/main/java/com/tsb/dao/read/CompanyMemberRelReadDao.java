package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.CompanyMemberRel;

public interface CompanyMemberRelReadDao {
	CompanyMemberRel get(Integer id);
	List<CompanyMemberRel> listByCompanyId(Integer companyId);
	List<CompanyMemberRel> listByMemberId(Integer memberId);
}
