package com.tsb.dao.write.user;

import com.tsb.model.user.User;

public interface UserWriteDao {
	void insert(User user);
	void update(User user);
}
