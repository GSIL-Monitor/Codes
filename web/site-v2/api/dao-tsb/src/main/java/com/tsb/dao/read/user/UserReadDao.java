package com.tsb.dao.read.user;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.user.User;

@SuppressWarnings("rawtypes")
public interface UserReadDao {
	User getById(Integer id);

	User getByEmail(String email);

	List<User> getByIds(@Param("ids") List ids);
	
	List<User> listByOrgAndRole(@Param("organizationId") int organizationId, @Param("role") int role);
	
}
