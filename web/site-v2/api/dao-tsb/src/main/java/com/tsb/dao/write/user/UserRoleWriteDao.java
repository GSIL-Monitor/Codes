package com.tsb.dao.write.user;


import com.tsb.model.user.UserRole;

public interface UserRoleWriteDao {
	
	void insert(UserRole userRole);
	void update(UserRole userRole);
	void delete(int id);
}
