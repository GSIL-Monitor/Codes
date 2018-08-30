package com.tsb.model.org;

import com.tsb.model.TimeModel;

public class Deal extends TimeModel {
	private Integer id;
	private Integer companyId;
	private Integer organizationId;
	private Integer status;
	private Integer priority;
	private Integer declineStatus;
	private Integer currency;
	private Integer preMoney;
	private Integer investment;
	private Integer type;

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

	public Integer getOrganizationId() {
		return organizationId;
	}

	public void setOrganizationId(Integer organizationId) {
		this.organizationId = organizationId;
	}

	public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}

	public Integer getPriority() {
		return priority;
	}

	public void setPriority(Integer priority) {
		this.priority = priority;
	}

	public Integer getDeclineStatus() {
		return declineStatus;
	}

	public void setDeclineStatus(Integer declineStatus) {
		this.declineStatus = declineStatus;
	}

	public Integer getCurrency() {
		return currency;
	}

	public void setCurrency(Integer currency) {
		this.currency = currency;
	}

	public Integer getPreMoney() {
		return preMoney;
	}

	public void setPreMoney(Integer preMoney) {
		this.preMoney = preMoney;
	}

	public Integer getInvestment() {
		return investment;
	}

	public void setInvestment(Integer investment) {
		this.investment = investment;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

}
