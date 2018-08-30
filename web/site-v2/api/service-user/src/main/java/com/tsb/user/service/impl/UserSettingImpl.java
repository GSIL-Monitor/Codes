package com.tsb.user.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.dao.read.user.UserSectorReadDao;
import com.tsb.dao.read.user.UserSettingReadDao;
import com.tsb.dao.write.user.UserSectorWriteDao;
import com.tsb.dao.write.user.UserSettingWriteDao;
import com.tsb.model.user.UserSetting;
import com.tsb.user.service.UserSectorService;
import com.tsb.user.service.UserSettingService;

@Service
public class UserSettingImpl implements UserSettingService{

	@Autowired
	private UserSettingReadDao userSettingReadDao;
	
	@Autowired
	private UserSettingWriteDao userSettingWriteDao;
	
	@Autowired
	private UserSectorService userSectorService;
	
	
	@Override
	public UserSetting get(int userId) {
		return userSettingReadDao.get(userId);
	}

	@Override
	public void update(int userId, int recommendNum) {
		UserSetting us = userSettingReadDao.get(userId);
		if(us == null){
			us = new UserSetting();
			us.setUserId(userId);
			us.setRecommendNum(recommendNum);
			userSettingWriteDao.insert(us);
		}else{
			us.setRecommendNum(recommendNum);
			userSettingWriteDao.update(us);
		}
	}

	@Override
	public void updateAll(int userId, int recommendNum, List newIds,
			List deleteIds) {
		update(userId, recommendNum);
		userSectorService.update(newIds, deleteIds, userId);
	}

}
