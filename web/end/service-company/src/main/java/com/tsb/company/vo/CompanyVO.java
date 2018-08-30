package com.tsb.company.vo;

import java.sql.Date;

public class CompanyVO {
	private Integer id;
	private String code;
	private String name;
	private String fullName;
	private String logo;
	private String brief;
	private String description;
	private String round;
	private String roundDesc;
	private Date establishDate;
	private String address;
	private String phone;
	private Integer preMoney;
	private Character verify;
	private Character active;

	private String location;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public String getCode() {
		return code;
	}

	public void setCode(String code) {
		this.code = code;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
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

	public String getRoundDesc() {
		return roundDesc;
	}

	public void setRoundDesc(String roundDesc) {
		this.roundDesc = roundDesc;
	}

	public Date getEstablishDate() {
		return establishDate;
	}

	public void setEstablishDate(Date establishDate) {
		this.establishDate = establishDate;
	}

	public String getAddress() {
		return address;
	}

	public void setAddress(String address) {
		this.address = address;
	}

	public String getPhone() {
		return phone;
	}

	public void setPhone(String phone) {
		this.phone = phone;
	}

	public Integer getPreMoney() {
		return preMoney;
	}

	public void setPreMoney(Integer preMoney) {
		this.preMoney = preMoney;
	}

	public Character getVerify() {
		return verify;
	}

	public void setVerify(Character verify) {
		this.verify = verify;
	}

	public Character getActive() {
		return active;
	}

	public void setActive(Character active) {
		this.active = active;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	public String getLogo() {
		return logo;
	}

	public void setLogo(String logo) {
		this.logo = logo;
	}
	
}
