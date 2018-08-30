package com.tsb.model.source;

import java.sql.Timestamp;

public class SourceBasicModel {
	private Character verify;
	private Timestamp createTime;
	private Timestamp modifyTime;
	public Character getVerify() {
		return verify;
	}
	public void setVerify(Character verify) {
		this.verify = verify;
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
	
}
