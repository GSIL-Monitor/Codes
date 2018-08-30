package com.tsb.enums;

public enum UserLogin {

	USERNAME(1, "username"),
	EMAIL(2, "email"),
	PHONE(3, "phone");
	
	Integer value;
	String name;
	
	private UserLogin(Integer value, String name){
		this.value = value;
		this.name = name;
	}
	
	
	public Integer getValue() {
		return value;
	}
	public void setValue(Integer value) {
		this.value = value;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	
	
}