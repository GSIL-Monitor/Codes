package com.tsb.enums;

public enum DealStatus {
	/** 19010 **/
	NEWDEAL(19010, "newDeal"),
	/** 19020 **/
	ACTIVEDEAL(19020, "activeDeal"),
	/** 19030 **/
	TERMSHEET(19030, "termsheet"),
	/** 19040 **/
	DD(19040, "dd"),
	/** 19050 **/
	PORTFOLIO(19050, "portfolio");

	private int value;
	private String name;

	private DealStatus(int value, String name) {
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
