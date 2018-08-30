package com.tsb.enums;

public enum FundingRound{

	UNKNOWN(300, "UNKNOWN"),
	ANGEL(301, "ANGEL"),
	PRE_A(302, "PRE_A"),
	A(303, "A"),
	B(304, "B"),
	C(305, "C"),
	D(306, "D"),
	E(307, "E"),
	LATE_STAGE(308, "LATE_STAGE"),
	PRE_IPO(309, "Pre-IPO"),
	IPO(310, "IPO");
	
	private int value;
	private String name;
	private FundingRound(int value, String name){
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
