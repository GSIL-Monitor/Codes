package com.tsb.model.dict;

public enum FollowStatus {
	
	NEW(1401, "New"),
	QUALIFIED(1402, "Qualified"),
	NEGOTIATION(1403, "Negotiation"),
	ACTIVE(1404, "Active"),
	PORTFOLIO(1405, "Portfolio"),
	PASSED(1406, "Passed");
	
	private int value;
	private String name;
	private FollowStatus(int value, String name){
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
