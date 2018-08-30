package com.crawler.model;

import java.sql.Timestamp;

public class NewsDomain {
	private int id;
	private String netloc;
	private String domain;
	private String title;
	private int appearCount;
	private int hintCount;
	private Character verify;
	private Character active;
	private Timestamp createTime;
	private Timestamp modifyTime;
	private int createUser;
	private int modifyUser;
	public int getId() {
		return id;
	}
	public void setId(int id) {
		this.id = id;
	}
	public String getNetloc() {
		return netloc;
	}
	public void setNetloc(String netloc) {
		this.netloc = netloc;
	}
	public String getDomain() {
		return domain;
	}
	public void setDomain(String domain) {
		this.domain = domain;
	}
	public String getTitle() {
		return title;
	}
	public void setTitle(String title) {
		this.title = title;
	}
	public int getAppearCount() {
		return appearCount;
	}
	public void setAppearCount(int appearCount) {
		this.appearCount = appearCount;
	}
	public int getHintCount() {
		return hintCount;
	}
	public void setHintCount(int hintCount) {
		this.hintCount = hintCount;
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
	public int getCreateUser() {
		return createUser;
	}
	public void setCreateUser(int createUser) {
		this.createUser = createUser;
	}
	public int getModifyUser() {
		return modifyUser;
	}
	public void setModifyUser(int modifyUser) {
		this.modifyUser = modifyUser;
	}
	
}
