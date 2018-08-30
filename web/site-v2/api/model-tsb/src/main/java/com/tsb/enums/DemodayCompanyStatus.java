package com.tsb.enums;

public enum DemodayCompanyStatus {
	/**初筛选中*/
	PRESCORING(27010, "preScoring"),
	/**初筛通过*/
	 PRESCORE_PAAS(27020, "preScore pass"),
	 /**初筛失败*/
	PRESCORE_FAILED(27030, "preScore failed"),
	/**打分中*/
	SCORING(27040, "scoring"),
	/**打分完成*/
	SCORE_DONE(27050, "score Done");
	
	private int value;
	private String name;
	private DemodayCompanyStatus(int value, String name){
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
