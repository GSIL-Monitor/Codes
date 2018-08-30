package com.tsb.model;

import java.sql.Timestamp;


public class TimeModel {
	private Timestamp createTime;
	private Timestamp modifyTime;
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
	
	
}
