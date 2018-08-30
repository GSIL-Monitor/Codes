package com.tsb.enums;

public enum DemodayStatus {
	/**项目提交**/
	SUBMMITTING(26000, "submmitting"),
	/**项目提交结束**/
	SUBMIT_END(26005,"submit end"),
	/**初筛选**/
	PRESCORING(26010, "preScoring"),
	/**筛选结束**/
	PRESCORE_DONE(26020, "preScore Done"),
	/**通知团队**/
	CONNECTTING_TEAM(26024,"connectting team"),
	/**通知团队结束**/
	CONNECTTING_TEAM_DONE(26027,"connectting team done"),
	/**进行中**/
	OPENING(26030, "opening"),
	/**完成**/
	DONE(26040, "done");
	
	private int value;
	private String name;
	private DemodayStatus(int value, String name){
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
