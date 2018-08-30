package com.tsb.dao.write.user;

import com.tsb.model.user.UserSetting;

public interface UserSettingWriteDao {
	void insert(UserSetting userSetting);
	void update(UserSetting userSetting);
}
