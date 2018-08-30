package com.crawler.model;

import java.sql.Timestamp;

public class CompanyIndex {
	private int id;
	private int companyId;
	private int alexa;
	private int android;
	private int ios;
	private int job;
	private int news;
	private int wechat;
	private Timestamp createTime;
	private Timestamp modifyTime;
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
	public int getAlexa() {
		return alexa;
	}
	public void setAlexa(int alexa) {
		this.alexa = alexa;
	}
	public int getAndroid() {
		return android;
	}
	public void setAndroid(int android) {
		this.android = android;
	}
	public int getIos() {
		return ios;
	}
	public void setIos(int ios) {
		this.ios = ios;
	}
	public int getJob() {
		return job;
	}
	public void setJob(int job) {
		this.job = job;
	}
	public int getNews() {
		return news;
	}
	public void setNews(int news) {
		this.news = news;
	}
	public int getWechat() {
		return wechat;
	}
	public void setWechat(int wechat) {
		this.wechat = wechat;
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
