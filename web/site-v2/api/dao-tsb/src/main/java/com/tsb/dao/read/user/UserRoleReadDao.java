package com.tsb.dao.read.user;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.user.UserRole;

public interface UserRoleReadDao {
	UserRole getByRole(@Param("userId")Integer userId, @Param("role")Integer role);
	@SuppressWarnings("rawtypes")
	List getRoles(int userId);
	List<UserRole> getUserRoles(int userId);
}
