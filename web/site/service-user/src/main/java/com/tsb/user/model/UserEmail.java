package com.tsb.user.model;

import java.io.Serializable;

import com.tsb.user.model.BasicModel;

public class UserEmail extends BasicModel implements Serializable{
	private static final long serialVersionUID = -1083138157154566310L;
	
	private int ueId;
	private int userId;
	private String randomCode;
	private int emailType;
	private Character active;
	public int getUeId() {
		return ueId;
	}
	public void setUeId(int ueId) {
		this.ueId = ueId;
	}
	public int getUserId() {
		return userId;
	}
	public void setUserId(int userId) {
		this.userId = userId;
	}
	public String getRandomCode() {
		return randomCode;
	}
	public void setRandomCode(String randomCode) {
		this.randomCode = randomCode;
	}
	public int getEmailType() {
		return emailType;
	}
	public void setEmailType(int emailType) {
		this.emailType = emailType;
	}
	public Character getActive() {
		return active;
	}
	public void setActive(Character active) {
		this.active = active;
	}
	
	
}
