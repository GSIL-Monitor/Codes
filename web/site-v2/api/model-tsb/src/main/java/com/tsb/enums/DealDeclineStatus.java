package com.tsb.enums;

public enum DealDeclineStatus {
	/** 正常跟进 18010 **/
	NORMAL(18010, "normal"),
	/** 归档 18015 **/
	ARCHIVE(18015, "archive"),
	/** 已经放弃 18020 **/
	DECLINE(18020, "decline");

	private int value;
	private String name;

	private DealDeclineStatus(int value, String name) {
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
