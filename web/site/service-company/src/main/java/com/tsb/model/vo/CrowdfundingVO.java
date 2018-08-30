package com.tsb.model.vo;

import java.util.List;

import com.tsb.model.crowdfunding.Crowdfunding;
import com.tsb.model.crowdfunding.SourceCfDocument;
import com.tsb.model.crowdfunding.SourceCfLeader;
import com.tsb.model.crowdfunding.SourceCrowdfunding;

public class CrowdfundingVO {
	private Crowdfunding crowdfunding;
	private SourceCrowdfunding sourceCrowdfunding;
	private List<SourceCfDocument> sourceCfDocumentList;
	private List<SourceCfLeader> sourceCfLeaderList;

	public Crowdfunding getCrowdfunding() {
		return crowdfunding;
	}

	public void setCrowdfunding(Crowdfunding crowdfunding) {
		this.crowdfunding = crowdfunding;
	}

	public SourceCrowdfunding getSourceCrowdfunding() {
		return sourceCrowdfunding;
	}

	public void setSourceCrowdfunding(SourceCrowdfunding sourceCrowdfunding) {
		this.sourceCrowdfunding = sourceCrowdfunding;
	}

	public List<SourceCfDocument> getSourceCfDocumentList() {
		return sourceCfDocumentList;
	}

	public void setSourceCfDocumentList(List<SourceCfDocument> sourceCfDocumentList) {
		this.sourceCfDocumentList = sourceCfDocumentList;
	}

	public List<SourceCfLeader> getSourceCfLeaderList() {
		return sourceCfLeaderList;
	}

	public void setSourceCfLeaderList(List<SourceCfLeader> sourceCfLeaderList) {
		this.sourceCfLeaderList = sourceCfLeaderList;
	}

}
