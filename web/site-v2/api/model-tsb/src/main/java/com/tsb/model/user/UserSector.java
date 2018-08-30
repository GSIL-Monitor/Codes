package com.tsb.model.user;

import com.tsb.model.BasicModel;

public class UserSector extends BasicModel{
	private Integer id;
	private Integer sectorId;
	private Integer userId;
	
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getSectorId() {
		return sectorId;
	}
	public void setSectorId(Integer sectorId) {
		this.sectorId = sectorId;
	}
	public Integer getUserId() {
		return userId;
	}
	public void setUserId(Integer userId) {
		this.userId = userId;
	}
}
