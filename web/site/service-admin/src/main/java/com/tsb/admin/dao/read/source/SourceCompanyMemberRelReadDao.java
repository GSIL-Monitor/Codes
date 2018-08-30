package com.tsb.admin.dao.read.source;

import java.util.List;

import com.tsb.model.source.SourceCompanyMemberRel;

public interface SourceCompanyMemberRelReadDao {
	SourceCompanyMemberRel get(Integer id);
	List<SourceCompanyMemberRel> listByCompanyMemberRelId(Integer id);
}
