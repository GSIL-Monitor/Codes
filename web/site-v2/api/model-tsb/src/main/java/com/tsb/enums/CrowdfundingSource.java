package com.tsb.enums;

public enum CrowdfundingSource {

	JD(13010, "JD"),
	KR36(13020, "36Kr"),
	ITJUZI(13030, "ITjuzi"),
	CHENGYEPU(13040, "ChengYePu"),
	LAGOU(13050, "LaGou"),
	NEITUI(13051, "NeiTui"),
	JOBTONG(13052, "JobTong"),
	ZHILIAN(13053, "ZhiLian"),
	//ZHILIAN(13054, "ZhiLian"),
	DEMOHOUR(13060, "DemoHour"),
	CYZONE(13070, "CyZone"),
	BAIDU(13080, "BaiDu"),
	HAOSOU(13081, "HaoSou");
	
	
	
	private int value;
	private String name;
	private CrowdfundingSource(int value, String name){
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
