package com.tsb.vo;

public class KafkaConstant {
	private String list;
	
	private static KafkaConstant instance;
	
	public static KafkaConstant getInstance(){
		return instance;
	}

	public void init(){
		instance = this;
	}
	
	//--------------------------------------
	public String getList() {
		return list;
	}

	public void setList(String list) {
		this.list = list;
	}
}
