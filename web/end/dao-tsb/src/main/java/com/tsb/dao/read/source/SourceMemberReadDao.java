package com.tsb.dao.read.source;

import java.util.List;

import com.tsb.model.source.SourceMember;

public interface SourceMemberReadDao {
	SourceMember get(Integer id);
	List<SourceMember> listByMemberId(Integer id);
	List<SourceMember> listByCompanyMemberRelId(Integer id);
}
