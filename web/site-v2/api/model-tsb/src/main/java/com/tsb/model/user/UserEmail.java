package com.tsb.model.user;

public class UserEmail {
	private Integer id;
	private Integer userId;
	private String email;
	private Boolean verify;
	private String verifyCode;
	
	
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getUserId() {
		return userId;
	}
	public void setUserId(Integer userId) {
		this.userId = userId;
	}
	public String getEmail() {
		return email;
	}
	public void setEmail(String email) {
		this.email = email;
	}
	public String getVerifyCode() {
		return verifyCode;
	}
	public void setVerifyCode(String verifyCode) {
		this.verifyCode = verifyCode;
	}
	public Boolean getVerify() {
		return verify;
	}
	public void setVerify(Boolean verify) {
		this.verify = verify;
	}
}
