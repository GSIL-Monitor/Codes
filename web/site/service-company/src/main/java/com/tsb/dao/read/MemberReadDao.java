package com.tsb.dao.read;

import com.tsb.model.Member;

public interface MemberReadDao {
	Member getById(Integer id);
}
