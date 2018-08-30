package com.tsb.model.org;

import java.sql.Timestamp;

public class Coldcall {
	private Integer id;
	private Integer organizationId;
	private Integer coldcallType;
	private String name;
	private String content;
	private String url;
	private Character processed;
	private Integer declineStatus;
	private Timestamp createTime;
	
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public Integer getOrganizationId() {
		return organizationId;
	}
	public void setOrganizationId(Integer organizationId) {
		this.organizationId = organizationId;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getContent() {
		return content;
	}
	public void setContent(String content) {
		this.content = content;
	}
	public Timestamp getCreateTime() {
		return createTime;
	}
	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}
	public Integer getColdcallType() {
		return coldcallType;
	}
	public void setColdcallType(Integer coldcallType) {
		this.coldcallType = coldcallType;
	}
	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}
	public Character getProcessed() {
		return processed;
	}
	public void setProcessed(Character processed) {
		this.processed = processed;
	}
	public Integer getDeclineStatus() {
		return declineStatus;
	}
	public void setDeclineStatus(Integer declineStatus) {
		this.declineStatus = declineStatus;
	}
	
}
