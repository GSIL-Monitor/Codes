package com.tsb.user.service;

import com.tsb.user.enums.LoginStatus;

public interface UserService {
	LoginStatus login(String email, String password, String ip, boolean isKeepLogin);
	LoginStatus login(int userid, String keeploginsecret, String ip);
	int resetpwd(int userId, String oneTimePwd, String newPassword);
	boolean checkAdmin(int userId);
}
