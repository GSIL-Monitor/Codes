package com.tsb.model.demoday;

import com.tsb.model.TimeModel;

public class DemodayPreScore extends TimeModel{
	private Integer id;
	private Integer userId;
	private Integer dealDemodayId;
	private Integer score;

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

	public Integer getDealDemodayId() {
		return dealDemodayId;
	}

	public void setDealDemodayId(Integer dealDemodayId) {
		this.dealDemodayId = dealDemodayId;
	}

	public Integer getScore() {
		return score;
	}

	public void setScore(Integer score) {
		this.score = score;
	}
}
