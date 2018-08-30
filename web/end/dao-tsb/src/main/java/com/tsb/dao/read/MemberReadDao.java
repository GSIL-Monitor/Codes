package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.Member;

public interface MemberReadDao {
	Member get(Integer id);
	List<Member> listByCompanyId(Integer companyId);
}
