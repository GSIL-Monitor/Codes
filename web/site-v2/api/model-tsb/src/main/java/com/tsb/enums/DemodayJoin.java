package com.tsb.enums;

public enum DemodayJoin {
	/** 联络中,28010 **/
	CONNECTING(28010, "connecting"),
	/** 不参加,28020 **/
	REJECT(28020, "reject"),
	/** 参加, 28030 **/
	JOIN(28030, "join"),
	/** 申请中,28040 **/
	PENDING(28040, "pending"),
	/** 申请通过,28050 **/
	PASS(28050, "pass");

	private int value;
	private String name;

	private DemodayJoin(int value, String name) {
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
