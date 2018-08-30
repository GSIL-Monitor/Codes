package com.tsb.user.service;

import java.util.List;

import com.tsb.model.user.UserSetting;

public interface UserSettingService {
	UserSetting get(int userId);
	void update(int userId, int recommendNum);
	
	void updateAll(int userId, int recommendNum, List newIds, List deleteIds);
}
