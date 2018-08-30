package com.tsb.enums;

public enum CollectionType {
	/**精选，39010**/
	SYS(39010, "sys"),
	/**热门推荐，39020**/
	HOT(39020, "hotRecommand"),
	/**自定义，39030**/
	CUSTOM(39030, "custom");
	
	private int value;
	private String name;

	private CollectionType(int value, String name) {
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
