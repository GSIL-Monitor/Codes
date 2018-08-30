package com.tsb.user.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

@SuppressWarnings("rawtypes")
public interface UserCompanyListRelReadDao {

	List getCompanyListIds(@Param("userId") Integer userId, @Param("start") int start);
	//overload
	List getclIdsByUserId(Integer userId);
}
