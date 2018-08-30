package com.tsb.util;

import java.util.Map;

public class RequestVO {
	private Integer userid;
	private Map payload;
	private String ip;
	
	public Integer getUserid() {
		return userid;
	}
	public void setUserid(Integer userid) {
		this.userid = userid;
	}
	public Map getPayload() {
		return payload;
	}
	public void setPayload(Map payload) {
		this.payload = payload;
	}
	public String getIp() {
		return ip;
	}
	public void setIp(String ip) {
		this.ip = ip;
	}
	
	
	
	
}
