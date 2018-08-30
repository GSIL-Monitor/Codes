package com.tsb.company.vo;

import java.sql.Date;

public class CompanySearchVO {
	private Integer id;
	private String code;
	private String name;
	private String brief;
	private String description;
	private String round;
	private Date establishDate;
	
	private String location;
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
	public String getBrief() {
		return brief;
	}
	public void setBrief(String brief) {
		this.brief = brief;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getRound() {
		return round;
	}
	public void setRound(String round) {
		this.round = round;
	}
	public String getLocation() {
		return location;
	}
	public void setLocation(String location) {
		this.location = location;
	}

	public Date getEstablishDate() {
		return establishDate;
	}
	public void setEstablishDate(Date establishDate) {
		this.establishDate = establishDate;
	}
	public String getCode() {
		return code;
	}
	public void setCode(String code) {
		this.code = code;
	}
	
	
	
}
