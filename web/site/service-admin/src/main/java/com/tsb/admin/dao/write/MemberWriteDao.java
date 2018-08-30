package com.tsb.admin.dao.write;

import com.tsb.model.Member;

public interface MemberWriteDao {
	void insert(Member member);
	void update(Member member);
}
