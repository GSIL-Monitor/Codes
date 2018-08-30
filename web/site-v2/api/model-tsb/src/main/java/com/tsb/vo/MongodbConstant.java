package com.tsb.vo;

public class MongodbConstant {
	private String host;
	private String fileDir;
	
	private static MongodbConstant instance;
	
	public static MongodbConstant getInstance(){
		return instance;
	}

	public void init(){
		instance = this;
	}
	
	//--------------------------------------
	public String getHost() {
		return host;
	}
	public void setHost(String host) {
		this.host = host;
	}
	public String getFileDir() {
		return fileDir;
	}
	public void setFileDir(String fileDir) {
		this.fileDir = fileDir;
	}
}
