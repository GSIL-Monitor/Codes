package com.tsb.model;

import java.sql.Timestamp;

public class BasicModel {
	private Float confidence;
	private Character verify;
	private Character active;
	private Timestamp createTime;
	private Timestamp modifyTime;
	private Integer createUser;
	private Integer modifyUser;
	public Float getConfidence() {
		return confidence;
	}
	public void setConfidence(Float confidence) {
		this.confidence = confidence;
	}
	public Character getVerify() {
		return verify;
	}
	public void setVerify(Character verify) {
		this.verify = verify;
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
	public Integer getCreateUser() {
		return createUser;
	}
	public void setCreateUser(Integer createUser) {
		this.createUser = createUser;
	}
	public Integer getModifyUser() {
		return modifyUser;
	}
	public void setModifyUser(Integer modifyUser) {
		this.modifyUser = modifyUser;
	}
}
