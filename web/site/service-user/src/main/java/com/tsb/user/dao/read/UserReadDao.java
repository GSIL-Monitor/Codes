package com.tsb.user.dao.read;

import org.apache.ibatis.annotations.Param;

import com.tsb.user.model.User;


public interface UserReadDao {

	User get(int userId);
	User getByUsername(@Param("username")String username, @Param("password") String password);
	User getByEmail(@Param("email")String email, @Param("password") String password);
	User getByPhone(@Param("phone")String phone, @Param("password") String password);
	User getUserSessionByUsername(String username);
	
	Boolean checkByUsername(String username);
	Boolean checkByEmail(String email);
	Boolean checkByPhone(String phone);
	
}
