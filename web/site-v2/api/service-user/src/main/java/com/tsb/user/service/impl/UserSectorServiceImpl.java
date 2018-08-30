package com.tsb.user.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.dao.read.user.UserSectorReadDao;
import com.tsb.dao.write.user.UserSectorWriteDao;
import com.tsb.model.company.Sector;
import com.tsb.model.user.UserSector;
import com.tsb.user.service.UserSectorService;

@Service
public class UserSectorServiceImpl implements UserSectorService{

	@Autowired
	private UserSectorReadDao userSectorReadDao;
	
	@Autowired
	private UserSectorWriteDao userSectorWriteDao;
	
	@Override
	public List<UserSector> get(Integer userId) {
		return userSectorReadDao.get(userId);
	}

	@Override
	public void add(List<Integer> sectorIds,Integer userId) {
		for(Integer id: sectorIds){
			Timestamp time = new Timestamp(System.currentTimeMillis());
			UserSector us = new UserSector();
			us.setSectorId(id);
			us.setUserId(userId);
			us.setActive('Y');
			us.setCreateTime(time);
			us.setCreateUser(userId);
			
			userSectorWriteDao.insert(us);
			
//			UserSector userSector =  userSectorReadDao.getBySectorId(id, userId);
//			if(userSector != null)
//				userSectorWriteDao.insert(us);
//			else
//				userSectorWriteDao.update(userSector);
		}
	}

	@Override
	public void delete(List<Integer> sectorIds, Integer userId) {
		for(Integer id: sectorIds){
			userSectorWriteDao.delete(userId, id);
		}
	}

	@Override
	public void update(List newIds, List deleteIds, int userId) {
		if(newIds !=null){
			if(newIds.size() > 0)
				add(newIds, userId);
		}
		
		if(deleteIds != null){
			if(deleteIds.size() > 0)
				delete(deleteIds, userId);
		}
	}

}
