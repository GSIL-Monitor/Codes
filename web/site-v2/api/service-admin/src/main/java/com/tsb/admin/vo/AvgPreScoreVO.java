package com.tsb.admin.vo;

import java.util.List;

public class AvgPreScoreVO {
	// company name
	private String name;
	// 平均分
	private float avg;
	// company id
	private Integer id;

	private Integer demodayCompanyId;

	private Integer scoringStatus;

	List<UserPreScoreVO> partnerPreScores;

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public float getAvg() {
		return avg;
	}

	public void setAvg(float avg) {
		this.avg = avg;
	}

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public List<UserPreScoreVO> getPartnerPreScores() {
		return partnerPreScores;
	}

	public void setPartnerPreScores(List<UserPreScoreVO> partnerPreScores) {
		this.partnerPreScores = partnerPreScores;
	}

	public Integer getDemodayCompanyId() {
		return demodayCompanyId;
	}

	public void setDemodayCompanyId(Integer demodayCompanyId) {
		this.demodayCompanyId = demodayCompanyId;
	}

	public Integer getScoringStatus() {
		return scoringStatus;
	}

	public void setScoringStatus(Integer scoringStatus) {
		this.scoringStatus = scoringStatus;
	}

}
