package com.tsb.enums;

public enum ListStatus {
	PRIVATE(1001, "Private"),
	PUBLIC(1002, "Public"),
	INACTIVE(1003, "Inactive");
	
	private int value;
	private String name;
	
	private ListStatus(int value, String name) {
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
