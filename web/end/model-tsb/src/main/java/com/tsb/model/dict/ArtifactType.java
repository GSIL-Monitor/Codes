package com.tsb.model.dict;

public enum ArtifactType {
	ALL(0, "All"),
	WEBSITE(4010, "Website"),
	WECHAT(4020, "Wechat"),
	WEIBO(4030, "Weibo"),
	ISO(4040, "Ios"),
	ANDROID(4050, "Android"),
	WINDOWSPHONE(4060, "WindowsPhone"),
	PC(4070, "Pc"),
	MAC(4080, "Mac");
	
	private int value;
	private String name;
	private ArtifactType(int value, String name){
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
