package com.tsb.enums;

public enum CompanyStatus {
	RUNNING(2010, "Running"),
	CLOSED_DOWN(2020, "Closed Down");

	private int value;
	private String name;

	private CompanyStatus(int value, String name) {
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
