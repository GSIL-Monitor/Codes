package com.crawler.model;

import java.sql.Date;
import java.sql.Timestamp;

public class News {
	private int id;
	private int companyId;
	private int domainId;
	private Date date;
	private String title;
	private String link;
	private Character confidence;
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
	public int getCompanyId() {
		return companyId;
	}
	public void setCompanyId(int companyId) {
		this.companyId = companyId;
	}
	public int getDomainId() {
		return domainId;
	}
	public void setDomainId(int domainId) {
		this.domainId = domainId;
	}
	public Date getDate() {
		return date;
	}
	public void setDate(Date date) {
		this.date = date;
	}
	public String getTitle() {
		return title;
	}
	public void setTitle(String title) {
		this.title = title;
	}
	public String getLink() {
		return link;
	}
	public void setLink(String link) {
		this.link = link;
	}
	public Character getConfidence() {
		return confidence;
	}
	public void setConfidence(Character confidence) {
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
