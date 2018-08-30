package com.tsb.admin.service;

import java.util.List;

import com.tsb.model.user.User;
public interface UserService {
	boolean getUser(String email);
	void addUser(Integer orgId, User user,List<Integer>roles);
	void deleteUser(Integer id ,Integer orgId);
	@SuppressWarnings("rawtypes")
	void update(User user,List roles);
}
