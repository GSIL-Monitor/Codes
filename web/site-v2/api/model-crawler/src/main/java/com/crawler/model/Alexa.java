package com.crawler.model;

import java.sql.Date;

public class Alexa {
	private int id;
	private int companyId;
	private int artifactId;
	private int rankCN;
	private int rankGlobal;
	private int dailyIP;
	private int dailyPV;
	private Date date;
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
	public int getArtifactId() {
		return artifactId;
	}
	public void setArtifactId(int artifactId) {
		this.artifactId = artifactId;
	}
	public int getRankCN() {
		return rankCN;
	}
	public void setRankCN(int rankCN) {
		this.rankCN = rankCN;
	}
	public int getRankGlobal() {
		return rankGlobal;
	}
	public void setRankGlobal(int rankGlobal) {
		this.rankGlobal = rankGlobal;
	}
	public int getDailyIP() {
		return dailyIP;
	}
	public void setDailyIP(int dailyIP) {
		this.dailyIP = dailyIP;
	}
	public int getDailyPV() {
		return dailyPV;
	}
	public void setDailyPV(int dailyPV) {
		this.dailyPV = dailyPV;
	}
	public Date getDate() {
		return date;
	}
	public void setDate(Date date) {
		this.date = date;
	}
	
	
}
