package com.tsb.user.service.impl;

import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.dao.read.user.UserReadDao;
import com.tsb.dao.read.user.UserRoleReadDao;
import com.tsb.dao.write.user.UserWriteDao;
import com.tsb.model.user.User;
import com.tsb.model.user.UserRole;
import com.tsb.user.enums.LoginStatus;
import com.tsb.user.service.UserService;
import com.tsb.util.MD5;
import com.tsb.util.RandomCodeFactory;

@Service
public class UserServiceImpl implements UserService {
	private final String SALT = "24114581331805856724";
	
	@Autowired
	private UserReadDao userReadDao;
	
	@Autowired
	private UserRoleReadDao userRoleReadDao;
	
	@Autowired 
	private UserWriteDao userWriteDao;

	
	@Override
	public LoginStatus login(String email, String password, String ip, boolean isKeepLogin) {
		System.out.println("email:" + email + ", password=" + password);
		if( password == null || "".equalsIgnoreCase(password) ) return LoginStatus.WRONGPASSWORD;
		
		User user = userReadDao.getByEmail(email);
		if( user == null) return LoginStatus.WRONGPASSWORD;
		if( user.getActive() == 'N') return LoginStatus.LOCKED;
		if( user.getActive() == 'D') return LoginStatus.DEMISSION;
		
		MD5 md5 = new MD5();
		String str = SALT + user.getId().intValue() + password;
		String md5Pwd = md5.getMD5ofUTF8Str(str);
		if( user.getPassword().equalsIgnoreCase(md5Pwd) ){
			if( user.getLoginFailTimes() > 0){
				user.setLoginFailTimes(0);
			}
			user.setLoginIP(ip);
			if ( isKeepLogin ){
				user.setKeepLoginSecret(RandomCodeFactory.generateMixed(32));
			}
			else{
				user.setKeepLoginSecret(null);
			}
			user.setLastLoginTime(new Date());
			user.setToken(RandomCodeFactory.generateMixed(32));
			user.setTokenTime(new Date());
			userWriteDao.update(user);
			return LoginStatus.SUCCESS;
		}
		
		user.setLoginFailTimes(user.getLoginFailTimes() + 1);
		if( user.getLoginFailTimes() >= 10 ) {
			user.setActive('N');
			user.setLoginFailTimes(0);
		}
		userWriteDao.update(user);
		return LoginStatus.WRONGPASSWORD;
	}

	@Override
	public LoginStatus login(int userid, String keeploginsecret, String ip){
		if( keeploginsecret == null || "".equalsIgnoreCase(keeploginsecret) ) return LoginStatus.WRONGPASSWORD;
		User user = userReadDao.getById(userid);
		if( user == null) return LoginStatus.WRONGPASSWORD;
		if( user.getActive() == 'N') return LoginStatus.LOCKED;
		if( user.getActive() == 'D') return LoginStatus.DEMISSION;
		
		if(user.getKeepLoginSecret() != null && user.getKeepLoginSecret().equals(keeploginsecret)){
			user.setLoginFailTimes(0);
			user.setLoginIP(ip);
			user.setLastLoginTime(new Date());
			user.setToken(RandomCodeFactory.generateMixed(32));
			user.setTokenTime(new Date());
			userWriteDao.update(user);
			return LoginStatus.SUCCESS;
		}
		return LoginStatus.WRONGPASSWORD;
	}

	@Override
	public int resetpwd(int userId, String oneTimePwd, String newPassword) {
		User user = userReadDao.getById(userId);
		if( user == null){
			return -2;
		}
		
		if( user.getActive() == 'D' ){
			return -4;
		}
		
		if(!oneTimePwd.equalsIgnoreCase(user.getOneTimePwd())){
			return -3;
		}
		
		MD5 md5 = new MD5();
		String str = SALT + user.getId().intValue() + newPassword;
		String md5Pwd = md5.getMD5ofUTF8Str(str);
		
		user.setPassword(md5Pwd);
		user.setOneTimePwd(null);
		user.setActive('Y');
		user.setLoginFailTimes(0);
		userWriteDao.update(user);
		
		return 0;
	}

	@Override
	public boolean checkAdmin(int userId) {
		UserRole userRole = userRoleReadDao.getByRole(userId, 25060);
		return userRole == null?false:true;
	}
}
