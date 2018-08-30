package com.tsb.model.demoday;

import java.sql.Timestamp;
import java.util.Date;

import com.tsb.model.TimeModel;

public class Demoday extends TimeModel {

	private Integer id;
	private String name;
	private Date submitEndDate;
	private Date preScoreStartDate;
	private Date preScoreEndDate;
	private Date connectStartDate;
	private Date connectEndDate;
	private Date holdStartDate;
	private Date holdEndDate;
	private Integer status;
	private Timestamp createTime;
	private Timestamp modifyTime;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public Date getSubmitEndDate() {
		return submitEndDate;
	}
	public void setSubmitEndDate(Date submitEndDate) {
		this.submitEndDate = submitEndDate;
	}
	public Date getPreScoreStartDate() {
		return preScoreStartDate;
	}
	public void setPreScoreStartDate(Date preScoreStartDate) {
		this.preScoreStartDate = preScoreStartDate;
	}
	public Date getPreScoreEndDate() {
		return preScoreEndDate;
	}
	public void setPreScoreEndDate(Date preScoreEndDate) {
		this.preScoreEndDate = preScoreEndDate;
	}
	public Date getConnectStartDate() {
		return connectStartDate;
	}
	public void setConnectStartDate(Date connectStartDate) {
		this.connectStartDate = connectStartDate;
	}
	public Date getConnectEndDate() {
		return connectEndDate;
	}
	public void setConnectEndDate(Date connectEndDate) {
		this.connectEndDate = connectEndDate;
	}
	public Date getHoldStartDate() {
		return holdStartDate;
	}
	public void setHoldStartDate(Date holdStartDate) {
		this.holdStartDate = holdStartDate;
	}
	public Date getHoldEndDate() {
		return holdEndDate;
	}
	public void setHoldEndDate(Date holdEndDate) {
		this.holdEndDate = holdEndDate;
	}
	public Integer getStatus() {
		return status;
	}
	public void setStatus(Integer status) {
		this.status = status;
	}
	public Timestamp getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}
	public Timestamp getModifyTime() {
		return modifyTime;
	}
	public void setModifyTime(Timestamp modifyTime) {
		this.modifyTime = modifyTime;
	}

}
