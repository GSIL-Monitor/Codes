package com.tsb.user.dao.write;

import com.tsb.user.model.User;

public interface UserWriteDao {
	void insert(User user);
	void updatePassword(User user);
}
