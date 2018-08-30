package com.tsb.enums;

public enum SearchBy {
	
	KEYWORDS(701, "KEYWORD"),
	LOCATION(702, "LOCATION"),
	INVESTOR(703, "INVESTOR"),
	STAGE(704, "STAGE"),
	//FINANCE(705, "FINANCE"),
	FOUNDED(706, "FOUNDED");
	
	private int value;
	private String name;
	
	private SearchBy(int value, String name) {
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
