package com.tsb.model.demoday;

import com.tsb.model.TimeModel;

public class DemodayScore extends TimeModel {
	private Integer id;
	private Integer dealDemodayId;
	private Integer userId;
	private Integer industry;
	private Integer team;
	private Integer product;
	private Integer gain;
	private Integer preMoney;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getDealDemodayId() {
		return dealDemodayId;
	}

	public void setDealDemodayId(Integer dealDemodayId) {
		this.dealDemodayId = dealDemodayId;
	}

	public Integer getUserId() {
		return userId;
	}

	public void setUserId(Integer userId) {
		this.userId = userId;
	}

	public Integer getIndustry() {
		return industry;
	}

	public void setIndustry(Integer industry) {
		this.industry = industry;
	}

	public Integer getTeam() {
		return team;
	}

	public void setTeam(Integer team) {
		this.team = team;
	}

	public Integer getProduct() {
		return product;
	}

	public void setProduct(Integer product) {
		this.product = product;
	}

	public Integer getGain() {
		return gain;
	}

	public void setGain(Integer gain) {
		this.gain = gain;
	}

	public Integer getPreMoney() {
		return preMoney;
	}

	public void setPreMoney(Integer preMoney) {
		this.preMoney = preMoney;
	}

}
