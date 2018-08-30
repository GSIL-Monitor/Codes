package com.tsb.model.crowdfunding;

import com.tsb.model.BasicModel;

public class CfComment extends BasicModel {

	private Integer id;
	private Integer cfId;
	private String comment;
	private String userName;
	private Integer userId;
	private Integer type;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getCfId() {
		return cfId;
	}

	public void setCfId(Integer cfId) {
		this.cfId = cfId;
	}

	public String getComment() {
		return comment;
	}

	public void setComment(String comment) {
		this.comment = comment;
	}

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public Integer getUserId() {
		return userId;
	}

	public void setUserId(Integer userId) {
		this.userId = userId;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

}
