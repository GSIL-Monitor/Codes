package com.tsb.dao.read.user;

import com.tsb.model.user.UserSetting;

public interface UserSettingReadDao {
	UserSetting get(int userId);
}
