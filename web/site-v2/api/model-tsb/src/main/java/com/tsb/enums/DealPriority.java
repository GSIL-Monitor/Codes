package com.tsb.enums;

public enum DealPriority {
	/** 20010 **/
	COLD(20010, "cold"),
	/** 20020 **/
	WARM(20020, "warm"),
	/** 20030 **/
	HOT(20030, "hot");

	private int value;
	private String name;

	private DealPriority(int value, String name) {
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
