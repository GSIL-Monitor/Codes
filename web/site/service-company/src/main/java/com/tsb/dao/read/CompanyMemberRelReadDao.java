package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.vo.MemberExperience;

public interface CompanyMemberRelReadDao {
	int count(int companyId);

	List<MemberExperience> getMemberExperience(int memberId);
}
