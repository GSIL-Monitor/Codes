package com.tsb.enums;

public enum DealType {
	/**用户自选 23010**/
	USER(23010, "user"),
	/**cold call  23020**/
	COLDCALL(23020, "coldcall"),
	/**机器推荐 23030**/
	RECOMMEND(23030, "recommend");
	
	private int value;
	private String name;
	private DealType(int value, String name){
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
