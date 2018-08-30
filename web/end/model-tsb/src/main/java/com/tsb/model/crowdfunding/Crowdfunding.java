package com.tsb.model.crowdfunding;

import java.sql.Date;

import com.tsb.model.BasicModel;

public class Crowdfunding extends BasicModel {

	private Integer id;
	private Integer companyId;
	private String name;
	private String description;
	private Integer amountRaising;
	private Integer successRaising;
	private Integer coinvestorCount;
	private Integer minInvestment;
	private Integer currency;
	private Date satartDate;
	private Date endDate;
	private Integer preMoney;
	private Integer postMoney;
	private Integer status;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Integer getAmountRaising() {
		return amountRaising;
	}

	public void setAmountRaising(Integer amountRaising) {
		this.amountRaising = amountRaising;
	}

	public Integer getSuccessRaising() {
		return successRaising;
	}

	public void setSuccessRaising(Integer successRaising) {
		this.successRaising = successRaising;
	}

	public Integer getCoinvestorCount() {
		return coinvestorCount;
	}

	public void setCoinvestorCount(Integer coinvestorCount) {
		this.coinvestorCount = coinvestorCount;
	}

	public Integer getMinInvestment() {
		return minInvestment;
	}

	public void setMinInvestment(Integer minInvestment) {
		this.minInvestment = minInvestment;
	}

	public Integer getCurrency() {
		return currency;
	}

	public void setCurrency(Integer currency) {
		this.currency = currency;
	}

	public Date getSatartDate() {
		return satartDate;
	}

	public void setSatartDate(Date satartDate) {
		this.satartDate = satartDate;
	}

	public Date getEndDate() {
		return endDate;
	}

	public void setEndDate(Date endDate) {
		this.endDate = endDate;
	}

	public Integer getPreMoney() {
		return preMoney;
	}

	public void setPreMoney(Integer preMoney) {
		this.preMoney = preMoney;
	}

	public Integer getPostMoney() {
		return postMoney;
	}

	public void setPostMoney(Integer postMoney) {
		this.postMoney = postMoney;
	}

	public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}
}
