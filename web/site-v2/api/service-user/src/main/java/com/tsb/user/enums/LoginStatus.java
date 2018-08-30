package com.tsb.user.enums;

public enum LoginStatus {
	SUCCESS(0),
	WRONGPASSWORD(1),
	LOCKED(2),
	DEMISSION(3);
	
	private final int value;
	
	private LoginStatus(int value) {
		this.value = value;
	}
	
	public Integer getValue() {
		return value;
	}
}
