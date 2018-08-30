package com.tsb.service.impl;

import java.sql.Timestamp;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.stereotype.Service;

import com.tsb.enums.UserLogin;
import com.tsb.service.UserService;
import com.tsb.user.dao.read.UserReadDao;
import com.tsb.user.dao.write.UserWriteDao;
import com.tsb.user.model.User;
import com.tsb.util.MD5;


@Service("UserService")
@EnableAsync
public class UserServiceImpl implements UserService {

	@Autowired
	private UserReadDao userReadDao;
	
	@Autowired
	private UserWriteDao userWriteDao;
	
	
	@Override
	public User getUser(String param, String password, Integer type) {
		User user = new User();
		
		MD5 md5 = new MD5();
		String newPwd = md5.getMD5ofUTF8Str(password);
		
		if(type == UserLogin.USERNAME.getValue()){
			user = userReadDao.getByUsername(param, newPwd);
		}
		else if (type == UserLogin.EMAIL.getValue()) {
			user = userReadDao.getByEmail(param, newPwd);
		}
		else if (type == UserLogin.PHONE.getValue()) {
			user = userReadDao.getByPhone(param, newPwd);
		}
		if(user != null)
			user.setPassword(null);
		
		return user;
	}

	@Override
	public boolean checkUser(String param, Integer type) {
		Boolean flag = false;
		if(type == UserLogin.USERNAME.getValue()){
			flag = userReadDao.checkByUsername(param);
		}
		else if (type == UserLogin.EMAIL.getValue()) {
			flag = userReadDao.checkByEmail(param);
		}
		else if (type == UserLogin.PHONE.getValue()) {
			flag = userReadDao.checkByPhone(param);
		}
		
		if (flag == null)
			flag = false;
		
		return flag;
	}

	@Override
	public User getUserSessionByUsername(String username) {
		User user =  userReadDao.getUserSessionByUsername(username);
		if(user != null)
			user.setPassword(null);
		
		return user;
	}

	@Override
	public void createUser(String username, String email, String password) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		MD5 md5 = new MD5();
		String newPwd = md5.getMD5ofUTF8Str(password);
		
		User user = new User();
		user.setUsername(username);
		user.setEmail(email);
		user.setPassword(newPwd);
		user.setCreateTime(time);
		user.setActive('P');
		
		userWriteDao.insert(user);
	}

}
