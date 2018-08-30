package com.tsb.user.model;

import java.io.Serializable;
import java.sql.Timestamp;

import com.tsb.user.model.BasicModel;

public class UserCompanyRel extends BasicModel implements Serializable{
	private static final long serialVersionUID = -3553568220670196386L;
	
	private int ucrId;
	private int userId;
	private int companyId;
	private String note;
	private Character heart;
	private int followStatus;
	private Timestamp followStart;
	
	public int getUcrId() {
		return ucrId;
	}
	public Timestamp getFollowStart() {
		return followStart;
	}
	public void setFollowStart(Timestamp followStart) {
		this.followStart = followStart;
	}
	public void setUcrId(int ucrId) {
		this.ucrId = ucrId;
	}
	public int getUserId() {
		return userId;
	}
	public void setUserId(int userId) {
		this.userId = userId;
	}
	public int getCompanyId() {
		return companyId;
	}
	public void setCompanyId(int companyId) {
		this.companyId = companyId;
	}
	public String getNote() {
		return note;
	}
	public void setNote(String note) {
		this.note = note;
	}
	public Character getHeart() {
		return heart;
	}
	public void setHeart(Character heart) {
		this.heart = heart;
	}
	public int getFollowStatus() {
		return followStatus;
	}
	public void setFollowStatus(int followStatus) {
		this.followStatus = followStatus;
	}

	
	
}
