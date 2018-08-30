package com.tsb.dao.read.crowdfunding;

import java.util.List;

import com.tsb.model.crowdfunding.SourceCfMember;

public interface SourceCfMemberReadDao {
	int count(Integer scfId);

	List<SourceCfMember> getMembers(Integer scfId);
}
