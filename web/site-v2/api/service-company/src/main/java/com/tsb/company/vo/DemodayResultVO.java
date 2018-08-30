package com.tsb.company.vo;

import java.util.List;

public class DemodayResultVO {
	// 有意向投资的org
	private List<DemodayOrgResultVO> orgResults;
	private List<DemodayAllUserScoreVO> scoreList;

	public List<DemodayOrgResultVO> getOrgResults() {
		return orgResults;
	}

	public void setOrgResults(List<DemodayOrgResultVO> orgResults) {
		this.orgResults = orgResults;
	}

	public List<DemodayAllUserScoreVO> getScoreList() {
		return scoreList;
	}

	public void setScoreList(List<DemodayAllUserScoreVO> scoreList) {
		this.scoreList = scoreList;
	}

}
