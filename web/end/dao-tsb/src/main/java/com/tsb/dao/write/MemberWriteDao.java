package com.tsb.dao.write;

import com.tsb.model.Member;

public interface MemberWriteDao {
	void insert(Member member);
	void update(Member member);
}
