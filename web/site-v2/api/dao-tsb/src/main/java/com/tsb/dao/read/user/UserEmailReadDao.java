package com.tsb.dao.read.user;

import com.tsb.model.user.UserEmail;

public interface UserEmailReadDao {
	UserEmail getByEmail(String email);
}
