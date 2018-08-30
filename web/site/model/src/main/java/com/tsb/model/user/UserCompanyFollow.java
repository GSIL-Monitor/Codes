package com.tsb.model.user;

import java.io.Serializable;
import java.sql.Date;

import com.tsb.model.BasicModel;

public class UserCompanyFollow extends BasicModel implements Serializable {
	
	private static final long serialVersionUID = 765240426846391830L;
	
	private Integer id;
	private Integer userId;
	private Integer companyId;
	private Date followDate;
	private Integer status;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getUserId() {
		return userId;
	}

	public void setUserId(Integer userId) {
		this.userId = userId;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public Date getFollowDate() {
		return followDate;
	}

	public void setFollowDate(Date followDate) {
		this.followDate = followDate;
	}

	public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}

}
