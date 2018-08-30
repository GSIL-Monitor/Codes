package com.tsb.user.model;

import java.io.Serializable;

import com.tsb.user.model.BasicModel;

public class UserSaveSearch extends BasicModel implements Serializable{
	private static final long serialVersionUID = 4618248862171035818L;
	
	private int ussId;
	private int userId;
	private String searchParams;
	private Character active;
	public int getUssId() {
		return ussId;
	}
	public void setUssId(int ussId) {
		this.ussId = ussId;
	}
	public int getUserId() {
		return userId;
	}
	public void setUserId(int userId) {
		this.userId = userId;
	}
	public String getSearchParams() {
		return searchParams;
	}
	public void setSearchParams(String searchParams) {
		this.searchParams = searchParams;
	}
	public Character getActive() {
		return active;
	}
	public void setActive(Character active) {
		this.active = active;
	}
	
	
}
