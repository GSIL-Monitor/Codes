package com.tsb.dao.read.org.user;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.user.ColdcallUserRel;

public interface ColdcallUserRelReadDao {
	ColdcallUserRel get(@Param("coldcallId") Integer coldcallId, @Param("userId") Integer userId);
}
