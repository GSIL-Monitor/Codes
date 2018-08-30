package com.tsb.enums;

public enum Market {
	SANLIULING(16010, "360"),
	BAIDU(16020, "baidu"),
	WANDOUJIA(16030, "wandoujia"),
	MYAPP(16040, "myapp"),
	IOS(16100, "android");
	
	private int value;
	private String name;
	private Market(int value, String name){
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
