package com.tsb.enums;

public enum ArtifactType {
	/** 4010 **/
	WEBSITE(4010, "website"),
	/** 4020 **/
	WECHAT(4020, "wechat"),
	/** 4030 **/
	WEIBO(4030, "weibo"),
	/** 4040 **/
	IOS(4040, "iOS"),
	/** 4050 **/
	ANDROID(4050, "android"),
	/** 4060 **/
	WINDOWS_PHONE(4060, "windowsPhone"),
	/** 4070 **/
	PC(4070, "pc"),
	/** 4080 **/
	MAC(4080, "mac"),
	/** 4099 **/
	OTHER(4099, "other");

	private int value;
	private String name;

	private ArtifactType(int value, String name) {
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
