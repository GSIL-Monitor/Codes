package com.tsb.service;

import com.tsb.user.model.User;

public interface UserService {
	//read
	User getUser(String param, String password, Integer type);
	boolean checkUser(String param, Integer type);
	User getUserSessionByUsername(String username); //for session
	
	//write
	void createUser(String username, String email, String password);
	
}
