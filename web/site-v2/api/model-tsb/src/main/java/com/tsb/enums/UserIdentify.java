package com.tsb.enums;

public enum UserIdentify {
	/** 21010 **/
	CREATOR(21010, "creator"),
	/** 21020 **/
	ASSIGNEE(21020, "assignee"),
	/** 21030 **/
	SPONSOR(21030, "sponsor");

	private int value;
	private String name;

	private UserIdentify(int value, String name) {
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
