package com.tsb.service.impl;

import java.sql.Date;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.model.dict.FollowStatus;
import com.tsb.model.user.UserCompanyFollow;
import com.tsb.model.user.UserCompanyNote;
import com.tsb.model.vo.FollowCompany;
import com.tsb.service.CompanyService;
import com.tsb.service.UserCompanyService;
import com.tsb.user.dao.read.UserCompanyFollowReadDao;
import com.tsb.user.dao.read.UserCompanyNoteReadDao;
import com.tsb.user.dao.write.UserCompanyFollowWriteDao;
import com.tsb.user.dao.write.UserCompanyNoteWriteDao;




@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class UserCompanyServiceImpl implements UserCompanyService {

	@Autowired
	private UserCompanyFollowReadDao ucfReadDao;
	@Autowired
	private UserCompanyFollowWriteDao ucfWriteDao;
	@Autowired
	private CompanyService companyService;
	@Autowired
	private UserCompanyNoteReadDao ucnReadDao;
	@Autowired
	private UserCompanyNoteWriteDao ucnWriteDao;

	@Override
	public List<FollowCompany> getFolCompaniesByStatus(Integer userId, int statusValue) {
		List<UserCompanyFollow> ucfList = new ArrayList<UserCompanyFollow>();
		if (statusValue == 0) {
			ucfList = ucfReadDao.getByUserId(userId);
		} else {
			ucfList = ucfReadDao.getByStatus(userId, statusValue);
		}
		List companyIds = new ArrayList();
		for (UserCompanyFollow ucf : ucfList) {
			companyIds.add(ucf.getCompanyId());
		}
		List<FollowCompany> followCompanyList = new ArrayList<FollowCompany>();
		if (companyIds.size() > 0) {
			followCompanyList = companyService.getFollowCompanies(userId, companyIds);
		}

		return followCompanyList;
	}

	@Override
	public void unfollow(Integer userId, List companyIds) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		
		for(int i=0 ,len=companyIds.size(); i<len; i++){
			UserCompanyFollow ucf = new UserCompanyFollow();
			ucf.setUserId(userId);
			ucf.setCompanyId((Integer)companyIds.get(i));
			ucf.setActive('N');
			ucf.setModifyTime(time);
			ucfWriteDao.update(ucf);
		}
	}

	@Override
	public UserCompanyFollow getByUserIdAndCompanyId(int userId, int companyId) {
		return ucfReadDao.getByUserIdAndCompanyId(userId, companyId);
	}

	@Override
	public void updateHeart(int userId, int companyId, Character heart) {
		Date time = new Date(System.currentTimeMillis());
		Timestamp cmTime = new Timestamp(System.currentTimeMillis());
		UserCompanyFollow ucf = ucfReadDao.getByUserIdAndCompanyId(userId, companyId);

		if (null == ucf) {
			UserCompanyFollow newUcf = new UserCompanyFollow();
			newUcf.setUserId(userId);
			newUcf.setCompanyId(companyId);
			newUcf.setActive(heart);
			newUcf.setStatus(FollowStatus.NEW.getValue());
			newUcf.setFollowDate(time);
			newUcf.setCreateTime(cmTime);
			ucfWriteDao.insert(newUcf);
		} else {
			ucf.setActive(heart);
			ucf.setModifyTime(cmTime);
			ucfWriteDao.update(ucf);
		}

	}

	@Override
	public UserCompanyNote getUserCompanyNote(int userId, int companyId) {
		
		return ucnReadDao.get(userId, companyId);
	}
	
	@Override
	public void updateFollowing(int userId, int companyId, int status, Date start) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		UserCompanyFollow ucf = ucfReadDao.getByUserIdAndCompanyId(userId, companyId);
		
		if(ucf == null){
			UserCompanyFollow newUcf = new UserCompanyFollow();
			newUcf.setUserId(userId);
			newUcf.setCompanyId(companyId);
			newUcf.setActive('Y');
			newUcf.setStatus(status);
			newUcf.setFollowDate(start);
			newUcf.setCreateTime(time);
			ucfWriteDao.insert(newUcf);
		}else{
			ucf.setActive('Y');
			ucf.setStatus(status);
			ucf.setFollowDate(start);
			ucf.setModifyTime(time);
			ucfWriteDao.updateStatsu(ucf);
		}
	}

	@Override
	public void updateNote(int userId, int companyId, String note) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		// 查询所有，包括active是否位Y
		UserCompanyNote ucn = ucnReadDao.getAll(userId, companyId);
		
		if(ucn == null){
			UserCompanyNote newUcn = new UserCompanyNote();
			newUcn.setUserId(userId);
			newUcn.setCompanyId(companyId);
			newUcn.setNote(note);
			newUcn.setActive('Y');
			newUcn.setCreateTime(time);
			ucnWriteDao.insert(newUcn);
		}else{
			ucn.setActive('Y');
			ucn.setNote(note);
			ucn.setModifyTime(time);
			ucnWriteDao.update(ucn);
		}
		
	}

}
