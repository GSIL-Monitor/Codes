package com.tsb.model.user;

import java.sql.Timestamp;
import java.util.Date;

public class User{

	private Integer id;
	private String username;
	private String email;
	private String phone;
	private String password;
	private String token;
	private Date tokenTime;
	private int loginFailTimes;
	private String loginIP;
	private String keepLoginSecret;
	private Date lastLoginTime;
	private String oneTimePwd;
	private Character active;
	private Timestamp createTime;
	private Timestamp modifyTime;
	
	
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public String getUsername() {
		return username;
	}
	public void setUsername(String username) {
		this.username = username;
	}
	public String getEmail() {
		return email;
	}
	public void setEmail(String email) {
		this.email = email;
	}
	public String getPhone() {
		return phone;
	}
	public void setPhone(String phone) {
		this.phone = phone;
	}
	public String getPassword() {
		return password;
	}
	public void setPassword(String password) {
		this.password = password;
	}
	public String getToken() {
		return token;
	}
	public void setToken(String token) {
		this.token = token;
	}
	public Date getTokenTime() {
		return tokenTime;
	}
	public void setTokenTime(Date tokenTime) {
		this.tokenTime = tokenTime;
	}
	public Character getActive() {
		return active;
	}
	public void setActive(Character active) {
		this.active = active;
	}
	public Timestamp getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}
	public Timestamp getModifyTime() {
		return modifyTime;
	}
	public void setModifyTime(Timestamp modifyTime) {
		this.modifyTime = modifyTime;
	}
	public int getLoginFailTimes() {
		return loginFailTimes;
	}
	public void setLoginFailTimes(int loginFailTimes) {
		this.loginFailTimes = loginFailTimes;
	}
	public String getLoginIP() {
		return loginIP;
	}
	public void setLoginIP(String loginIP) {
		this.loginIP = loginIP;
	}
	public String getKeepLoginSecret() {
		return keepLoginSecret;
	}
	public void setKeepLoginSecret(String keepLoginSecret) {
		this.keepLoginSecret = keepLoginSecret;
	}
	public Date getLastLoginTime() {
		return lastLoginTime;
	}
	public void setLastLoginTime(Date lastLoginTime) {
		this.lastLoginTime = lastLoginTime;
	}
	public String getOneTimePwd() {
		return oneTimePwd;
	}
	public void setOneTimePwd(String oneTimePwd) {
		this.oneTimePwd = oneTimePwd;
	}
}
