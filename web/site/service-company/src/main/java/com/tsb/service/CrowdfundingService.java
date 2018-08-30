package com.tsb.service;

import java.util.List;

import com.tsb.model.crowdfunding.SourceCfMember;
import com.tsb.model.crowdfunding.SourceCrowdfunding;
import com.tsb.model.vo.CfHeadVO;
import com.tsb.model.vo.CrowdfundingVO;

public interface CrowdfundingService {
	CrowdfundingVO getById(Integer cfId);

	List<SourceCrowdfunding> getByPage(int page, int status, int source);

	int count(int status, int source);

	CfHeadVO getCfHeadVOInfo(Integer scfId);

	List<SourceCfMember> getMembers(Integer scfId);

}
