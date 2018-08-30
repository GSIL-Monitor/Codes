package com.tsb.enums;

public enum CrowdfundingStatus {

	READY(14010, "Ready"),
	RAISING(14020, "Raising"),
	CLOSED(14030,"Closed");
//	SUCCESS_RAISING(14030, "SuccessRaising"),
//	SUCCEED(14040, "Succeed"),
//	FAILED(14050, "Failed");
	
	private int value;
	private String name;
	private CrowdfundingStatus(int value, String name){
		this.value = value;
		this.name = name;
	}
	public int getValue() {
		return value;
	}
	public void setValue(int value) {
		this.value = value;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	
}
